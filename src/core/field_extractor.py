"""Deterministic & Hybrid Field Extraction Engine for FormFlow.

Combines label-context matching, regular expressions, configurable templates,
and candidate ranking with evidence tracing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.core.pdf_parser import PageData, WordBox


@dataclass
class CandidateField:
    field_name: str
    extracted_value: Optional[str]
    normalized_value: Optional[str]
    data_type: str
    source_page: int
    evidence_excerpt: Optional[str]
    bounding_box: Optional[Dict[str, float]]
    extraction_method: str
    validation_status: str
    review_status: str
    confidence_note: Optional[str] = None
    alternative_candidates: List[str] = field(default_factory=list)


# Standard Regular Expression Patterns
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Phone patterns supporting international (+91, +1, etc.) and formatted national
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"
)

# Date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, and Textual like '15 Oct 2026' or 'October 15, 2026'
DATE_REGEX = re.compile(
    r"\b(?:\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?),?\s+\d{4})\b",
    re.IGNORECASE,
)

# Currency and amounts ($1,234.50, EUR 500, Rs. 1500, INR 25000, 1,450.00)
AMOUNT_REGEX = re.compile(
    r"(?:[\$€£₹]|USD|EUR|GBP|INR|Rs\.?)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|[0-9]+(?:\.[0-9]{2})?)\b|"
    r"\b([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})\b"
)

# Organization / Company suffix heuristic
ORG_SUFFIX_REGEX = re.compile(
    r"\b[A-Z][A-Za-z0-9\s&,.-]{2,40}?(?:\bInc\.?|\bLLC\b|\bCorp\.?|\bCorporation\b|\bLtd\.?|\bLimited\b|\bSolutions\b|\bTechnologies\b|\bServices\b|\bEnterprises\b|\bLab\b|\bUniversity\b|\bConsortium\b|\bBank\b)\b",
    re.IGNORECASE,
)

# Invoice / Order / Reference Number: match full identifier including prefix
ID_CODE_REGEX = re.compile(r"\b(?:INV|REF|APP|ORD|REG|POL|NO|ID)[-:#\s]*[A-Z0-9_-]{3,20}\b", re.IGNORECASE)


class FieldExtractor:
    """Extracts structured fields from extracted pages using templates, context anchors, and regex."""

    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        self.custom_rules = custom_rules or []

    @staticmethod
    def _find_bounding_box_for_text(text_snippet: str, words: List[WordBox]) -> Optional[Dict[str, float]]:
        """Find the approximate bounding box matching a snippet in the page word boxes."""
        if not text_snippet or not words:
            return None

        clean_snippet = re.sub(r"[^\w\s]", "", text_snippet).strip().lower()
        if not clean_snippet:
            return None

        tokens = clean_snippet.split()
        if not tokens:
            return None

        first_token = tokens[0]
        for i, w in enumerate(words):
            w_clean = re.sub(r"[^\w]", "", w.text).lower()
            if w_clean == first_token:
                # Check consecutive tokens
                matched = True
                end_idx = i
                for offset, t in enumerate(tokens[1:], start=1):
                    if i + offset >= len(words):
                        matched = False
                        break
                    next_clean = re.sub(r"[^\w]", "", words[i + offset].text).lower()
                    if next_clean != t:
                        matched = False
                        break
                    end_idx = i + offset

                if matched:
                    x0 = min(words[k].x0 for k in range(i, end_idx + 1))
                    top = min(words[k].top for k in range(i, end_idx + 1))
                    x1 = max(words[k].x1 for k in range(i, end_idx + 1))
                    bottom = max(words[k].bottom for k in range(i, end_idx + 1))
                    return {"x0": round(x0, 2), "top": round(top, 2), "x1": round(x1, 2), "bottom": round(bottom, 2)}

        return None

    @staticmethod
    def _extract_after_label(line: str, label_variants: List[str]) -> Optional[str]:
        """Extract value occurring immediately after a label keyword on the same line."""
        for lab in label_variants:
            pattern = re.compile(rf"(?:^|\b){re.escape(lab)}[\s:：#\-_=\.]+(.+)$", re.IGNORECASE)
            match = pattern.search(line)
            if match:
                val = match.group(1).strip()
                # Remove trailing noise
                val = re.sub(r"[\s|;]+$", "", val)
                if val:
                    return val
        return None

    def extract_fields(
        self,
        pages: List[PageData],
        template_rules: Optional[Dict[str, Any]] = None,
    ) -> List[CandidateField]:
        """Execute extraction across all document pages and consolidate candidate fields."""
        results: List[CandidateField] = []
        rules = template_rules.get("fields", {}) if template_rules else {}

        # Aggregate full text and page-indexed lines
        page_lines: List[Tuple[int, str]] = []
        for p in pages:
            text_to_use = p.ocr_text if (p.ocr_applied and p.ocr_text) else p.text
            for line in text_to_use.splitlines():
                stripped = line.strip()
                if stripped:
                    page_lines.append((p.page_number, stripped))

        # 1. Invoice Number / Reference Number
        inv_labels = rules.get("invoice_number", {}).get("aliases", [
            "invoice number", "invoice no", "invoice #", "inv no", "inv #", "bill no", "receipt no", "reference no"
        ])
        inv_val, inv_page, inv_excerpt, inv_alts = self._extract_labeled_or_regex(
            page_lines, inv_labels, ID_CODE_REGEX, default_pattern=r"^[A-Z0-9-]{3,20}$"
        )
        if inv_val or "invoice_number" in rules:
            results.append(
                CandidateField(
                    field_name="invoice_number",
                    extracted_value=inv_val,
                    normalized_value=inv_val.upper() if inv_val else None,
                    data_type="string",
                    source_page=inv_page,
                    evidence_excerpt=inv_excerpt,
                    bounding_box=self._find_bbox(pages, inv_page, inv_val),
                    extraction_method="context_label" if inv_excerpt else "regex",
                    validation_status="valid" if inv_val else "missing",
                    review_status="pending",
                    confidence_note=f"Found with {len(inv_alts)} alternatives." if inv_alts else "Deterministic match.",
                    alternative_candidates=inv_alts,
                )
            )

        # 2. Date
        date_labels = rules.get("date", {}).get("aliases", [
            "date", "invoice date", "issue date", "bill date", "application date", "dated", "registered on"
        ])
        date_val, date_page, date_excerpt, date_alts = self._extract_labeled_or_regex(
            page_lines, date_labels, DATE_REGEX
        )
        if date_val or "date" in rules:
            results.append(
                CandidateField(
                    field_name="date",
                    extracted_value=date_val,
                    normalized_value=date_val,
                    data_type="date",
                    source_page=date_page,
                    evidence_excerpt=date_excerpt,
                    bounding_box=self._find_bbox(pages, date_page, date_val),
                    extraction_method="context_label" if date_excerpt else "regex",
                    validation_status="valid" if date_val else "missing",
                    review_status="pending",
                    confidence_note=f"Parsed from text ({len(date_alts)} candidates)." if date_alts else "Context match.",
                    alternative_candidates=date_alts,
                )
            )

        # 3. Person / Applicant / Customer Name
        name_labels = rules.get("person_name", {}).get("aliases", [
            "name", "full name", "applicant name", "customer name", "bill to", "client name", "candidate name", "member name"
        ])
        name_val, name_page, name_excerpt, name_alts = self._extract_labeled_or_regex(
            page_lines, name_labels, None
        )
        if name_val or "person_name" in rules:
            # Clean common prefixes like 'Mr.', 'Ms.', 'Dr.'
            clean_name = re.sub(r"^(?:mr|ms|mrs|dr|prof)\.?\s+", "", name_val, flags=re.IGNORECASE).strip() if name_val else None
            results.append(
                CandidateField(
                    field_name="person_name",
                    extracted_value=clean_name,
                    normalized_value=clean_name.title() if clean_name else None,
                    data_type="string",
                    source_page=name_page,
                    evidence_excerpt=name_excerpt,
                    bounding_box=self._find_bbox(pages, name_page, clean_name),
                    extraction_method="context_label" if clean_name else "missing",
                    validation_status="valid" if clean_name else "missing",
                    review_status="pending",
                    confidence_note="Extracted from labeled anchor." if clean_name else "Label not detected.",
                    alternative_candidates=name_alts,
                )
            )

        # 4. Email Address
        email_labels = rules.get("email", {}).get("aliases", ["email", "e-mail", "email address", "contact email"])
        email_val, email_page, email_excerpt, email_alts = self._extract_labeled_or_regex(
            page_lines, email_labels, EMAIL_REGEX
        )
        if email_val or "email" in rules:
            results.append(
                CandidateField(
                    field_name="email",
                    extracted_value=email_val,
                    normalized_value=email_val.lower() if email_val else None,
                    data_type="email",
                    source_page=email_page,
                    evidence_excerpt=email_excerpt,
                    bounding_box=self._find_bbox(pages, email_page, email_val),
                    extraction_method="context_label" if email_excerpt else "regex",
                    validation_status="valid" if email_val else "missing",
                    review_status="pending",
                    confidence_note=f"Standard RFC regex pattern ({len(email_alts)} candidates)." if email_alts else "Unique email found.",
                    alternative_candidates=email_alts,
                )
            )

        # 5. Phone Number
        phone_labels = rules.get("phone", {}).get("aliases", ["phone", "phone number", "tel", "mobile", "contact no", "telephone"])
        phone_val, phone_page, phone_excerpt, phone_alts = self._extract_labeled_or_regex(
            page_lines, phone_labels, PHONE_REGEX
        )
        if phone_val or "phone" in rules:
            results.append(
                CandidateField(
                    field_name="phone",
                    extracted_value=phone_val,
                    normalized_value=phone_val,
                    data_type="phone",
                    source_page=phone_page,
                    evidence_excerpt=phone_excerpt,
                    bounding_box=self._find_bbox(pages, phone_page, phone_val),
                    extraction_method="context_label" if phone_excerpt else "regex",
                    validation_status="valid" if phone_val else "missing",
                    review_status="pending",
                    confidence_note="Phone number pattern.",
                    alternative_candidates=phone_alts,
                )
            )

        # 6. Organization / Company / Vendor
        org_labels = rules.get("organization", {}).get("aliases", [
            "company", "organization", "vendor", "vendor name", "provider", "institution", "employer"
        ])
        org_val, org_page, org_excerpt, org_alts = self._extract_labeled_or_regex(
            page_lines, org_labels, ORG_SUFFIX_REGEX
        )
        if org_val or "organization" in rules:
            results.append(
                CandidateField(
                    field_name="organization",
                    extracted_value=org_val,
                    normalized_value=org_val,
                    data_type="string",
                    source_page=org_page,
                    evidence_excerpt=org_excerpt,
                    bounding_box=self._find_bbox(pages, org_page, org_val),
                    extraction_method="context_label" if org_excerpt and not any(k in org_excerpt.lower() for k in ("inc", "corp", "llc", "ltd")) else "heuristic_suffix",
                    validation_status="valid" if org_val else "missing",
                    review_status="pending",
                    confidence_note="Corporate entity pattern detected." if org_val else "Organization not detected.",
                    alternative_candidates=org_alts,
                )
            )

        # 7. Total Amount / Monetary Amount
        amount_labels = rules.get("total_amount", {}).get("aliases", [
            "total", "total amount", "grand total", "net amount", "balance due", "amount", "fee", "registration fee"
        ])
        amt_val, amt_page, amt_excerpt, amt_alts = self._extract_labeled_or_regex(
            page_lines, amount_labels, AMOUNT_REGEX
        )
        if amt_val or "total_amount" in rules:
            results.append(
                CandidateField(
                    field_name="total_amount",
                    extracted_value=amt_val,
                    normalized_value=amt_val,
                    data_type="monetary",
                    source_page=amt_page,
                    evidence_excerpt=amt_excerpt,
                    bounding_box=self._find_bbox(pages, amt_page, amt_val),
                    extraction_method="context_label" if amt_excerpt else "regex",
                    validation_status="valid" if amt_val else "missing",
                    review_status="pending",
                    confidence_note=f"Ranked highest financial token ({len(amt_alts)} alternatives)." if amt_alts else "Deterministic amount.",
                    alternative_candidates=amt_alts,
                )
            )

        # 8. Address
        addr_labels = rules.get("address", {}).get("aliases", [
            "address", "billing address", "shipping address", "residence", "location"
        ])
        addr_val, addr_page, addr_excerpt, addr_alts = self._extract_labeled_or_regex(
            page_lines, addr_labels, None
        )
        if addr_val or "address" in rules:
            results.append(
                CandidateField(
                    field_name="address",
                    extracted_value=addr_val,
                    normalized_value=addr_val,
                    data_type="string",
                    source_page=addr_page,
                    evidence_excerpt=addr_excerpt,
                    bounding_box=self._find_bbox(pages, addr_page, addr_val),
                    extraction_method="context_label" if addr_val else "missing",
                    validation_status="valid" if addr_val else "missing",
                    review_status="pending",
                    confidence_note="Extracted from address label.",
                    alternative_candidates=addr_alts,
                )
            )

        # 9. Custom Template-Defined Fields
        standard_keys = {
            "invoice_number", "date", "person_name", "email", "phone",
            "organization", "total_amount", "address"
        }
        for field_key, field_spec in rules.items():
            if field_key in standard_keys:
                continue

            aliases = field_spec.get("aliases", [field_key.replace("_", " ")])
            pattern_str = field_spec.get("pattern")
            compiled_pat = None
            if pattern_str:
                try:
                    compiled_pat = re.compile(pattern_str, re.IGNORECASE)
                except re.error:
                    pass

            c_val, c_page, c_excerpt, c_alts = self._extract_labeled_or_regex(
                page_lines, aliases, compiled_pat
            )

            results.append(
                CandidateField(
                    field_name=field_key,
                    extracted_value=c_val,
                    normalized_value=c_val,
                    data_type=field_spec.get("data_type", "string"),
                    source_page=c_page,
                    evidence_excerpt=c_excerpt,
                    bounding_box=self._find_bbox(pages, c_page, c_val),
                    extraction_method="template_rule",
                    validation_status="valid" if c_val else ("missing" if field_spec.get("required") else "unverified"),
                    review_status="pending",
                    confidence_note=f"Custom rule match: {aliases[0]}",
                    alternative_candidates=c_alts,
                )
            )

        return results

    def _extract_labeled_or_regex(
        self,
        page_lines: List[Tuple[int, str]],
        label_variants: List[str],
        regex_fallback: Optional[re.Pattern] = None,
        default_pattern: Optional[str] = None,
    ) -> Tuple[Optional[str], int, Optional[str], List[str]]:
        """Search page lines for label match first, then fall back to deterministic regex ranking."""
        candidates: List[Tuple[str, int, str, int]] = []  # (value, page_num, excerpt, priority_score)

        # Pass 1: Labeled context match (highest priority score = 100)
        for page_num, line in page_lines:
            val = self._extract_after_label(line, label_variants)
            if val:
                # If a regex filter is specified, check compatibility
                if regex_fallback:
                    match = regex_fallback.search(val)
                    if match:
                        matched_str = match.group(0).strip()
                        candidates.append((matched_str, page_num, line, 100))
                    else:
                        candidates.append((val, page_num, line, 90))
                else:
                    candidates.append((val, page_num, line, 100))

        # Pass 2: If no labeled match and regex fallback is provided, scan all lines
        if not candidates and regex_fallback:
            for page_num, line in page_lines:
                for match in regex_fallback.finditer(line):
                    matched_str = match.group(0).strip()
                    if matched_str and len(matched_str) > 1:
                        candidates.append((matched_str, page_num, line, 50))

        if not candidates:
            return None, 1, None, []

        # Sort by priority score descending, then by first occurrence
        candidates.sort(key=lambda c: c[3], reverse=True)
        best_val, best_page, best_excerpt, _ = candidates[0]
        alt_values = list(dict.fromkeys(c[0] for c in candidates[1:] if c[0] != best_val))

        return best_val, best_page, best_excerpt, alt_values

    @staticmethod
    def _find_bbox(pages: List[PageData], page_num: int, val: Optional[str]) -> Optional[Dict[str, float]]:
        if not val or page_num < 1 or page_num > len(pages):
            return None
        target_page = pages[page_num - 1]
        return FieldExtractor._find_bounding_box_for_text(val, target_page.words)
