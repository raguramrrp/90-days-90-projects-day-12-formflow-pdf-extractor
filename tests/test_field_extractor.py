"""Tests for Deterministic and Hybrid Field Extraction."""

from __future__ import annotations

import pytest

from src.core.field_extractor import FieldExtractor
from src.core.pdf_parser import PageData, WordBox


def make_page(text: str, page_num: int = 1) -> PageData:
    words = []
    lines = text.splitlines()
    for row_idx, l in enumerate(lines):
        for col_idx, token in enumerate(l.split()):
            words.append(
                WordBox(
                    text=token,
                    x0=col_idx * 50.0,
                    top=row_idx * 20.0,
                    x1=(col_idx + 1) * 50.0,
                    bottom=(row_idx + 1) * 20.0,
                )
            )
    return PageData(
        page_number=page_num,
        width=612.0,
        height=792.0,
        text=text,
        char_count=len(text),
        word_count=len(words),
        is_scanned_candidate=False,
        words=words,
    )


class TestFieldExtractor:
    def setup_method(self):
        self.extractor = FieldExtractor()

    def test_labeled_anchor_extraction(self):
        sample_text = (
            "COMPANY: Horizon Logistics Inc.\n"
            "INVOICE NUMBER: INV-2026-9042\n"
            "INVOICE DATE: 2026-10-18\n"
            "BILL TO: Arthur Dent\n"
            "CONTACT EMAIL: arthur.dent@galaxy.org\n"
            "PHONE: +1-555-424-2424\n"
            "TOTAL AMOUNT: $3,450.00\n"
            "ADDRESS: 42 Magrathea Way, Sector 7\n"
        )
        page = make_page(sample_text)
        fields = self.extractor.extract_fields([page])

        field_dict = {f.field_name: f.extracted_value for f in fields}
        assert field_dict.get("invoice_number") == "INV-2026-9042"
        assert field_dict.get("date") == "2026-10-18"
        assert field_dict.get("person_name") == "Arthur Dent"
        assert field_dict.get("email") == "arthur.dent@galaxy.org"
        assert field_dict.get("phone") == "+1-555-424-2424"
        assert field_dict.get("total_amount") == "$3,450.00"
        assert "Horizon Logistics" in (field_dict.get("organization") or "")

    def test_regex_fallback_extraction_without_exact_labels(self):
        sample_text = (
            "Please send the response directly to contact@datascience.io by 2026-11-30.\n"
            "If questions arise, reach us at (415) 555-9081.\n"
            "Estimated project cost is $12,500.00.\n"
        )
        page = make_page(sample_text)
        fields = self.extractor.extract_fields([page])

        field_dict = {f.field_name: f.extracted_value for f in fields}
        assert field_dict.get("email") == "contact@datascience.io"
        assert "2026-11-30" in (field_dict.get("date") or "")
        assert "(415) 555-9081" in (field_dict.get("phone") or "")
        assert "12,500.00" in (field_dict.get("total_amount") or "")

    def test_candidate_ranking_with_multiple_values(self):
        sample_text = (
            "Support Email: support@generic.com\n"
            "Candidate Email Address: primary.user@enterprise.org\n"
            "Alternate: info@other.com\n"
        )
        page = make_page(sample_text)
        fields = self.extractor.extract_fields([page])
        email_field = next((f for f in fields if f.field_name == "email"), None)

        assert email_field is not None
        assert email_field.extracted_value in ("primary.user@enterprise.org", "support@generic.com")
        # Ensure alternative candidates were preserved
        assert len(email_field.alternative_candidates) >= 1

    def test_custom_template_fields(self):
        sample_text = (
            "Patient Name: Jane Doe\n"
            "Medical Record Number: MRN-88421\n"
            "Insurance Group: GRP-AZ-99\n"
        )
        page = make_page(sample_text)
        custom_rules = {
            "fields": {
                "medical_record_number": {
                    "aliases": ["medical record number", "mrn", "patient mrn"],
                    "data_type": "string",
                    "required": True,
                },
                "insurance_group": {
                    "aliases": ["insurance group", "grp no"],
                    "data_type": "string",
                    "required": False,
                },
            }
        }
        fields = self.extractor.extract_fields([page], template_rules=custom_rules)
        field_dict = {f.field_name: f.extracted_value for f in fields}

        assert field_dict.get("medical_record_number") == "MRN-88421"
        assert field_dict.get("insurance_group") == "GRP-AZ-99"
