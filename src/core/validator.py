"""Validation and Normalization Engine for FormFlow."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from dateutil import parser as date_parser

from src.core.field_extractor import EMAIL_REGEX


@dataclass
class ValidationResult:
    is_valid: bool
    status: str  # 'valid', 'warning', 'invalid', 'missing', 'unverified', 'corrected'
    normalized_value: Optional[str]
    message: str


class FieldValidator:
    """Validates and normalizes extracted field values based on data types and rules."""

    @classmethod
    def validate_field(
        cls,
        field_name: str,
        value: Optional[str],
        data_type: str = "string",
        required: bool = False,
        custom_regex: Optional[str] = None,
        is_user_corrected: bool = False,
    ) -> ValidationResult:
        """Execute type-aware validation, returning a detailed ValidationResult."""
        # 1. Check empty / missing values
        clean_val = value.strip() if value is not None else ""
        if not clean_val:
            if required:
                return ValidationResult(
                    is_valid=False,
                    status="missing",
                    normalized_value=None,
                    message=f"Required field '{field_name}' is missing.",
                )
            return ValidationResult(
                is_valid=True,
                status="unverified",
                normalized_value=None,
                message="Optional field is empty.",
            )

        # 2. Custom Regex Validation if provided
        if custom_regex:
            try:
                pattern = re.compile(custom_regex)
                if not pattern.search(clean_val):
                    return ValidationResult(
                        is_valid=False,
                        status="invalid",
                        normalized_value=clean_val,
                        message=f"Value does not match required pattern '{custom_regex}'.",
                    )
            except re.error as e:
                return ValidationResult(
                    is_valid=False,
                    status="warning",
                    normalized_value=clean_val,
                    message=f"Custom validation regex error: {e}",
                )

        # 3. Type-Specific Validation & Normalization
        dtype = data_type.lower()
        if dtype == "email":
            return cls._validate_email(clean_val, is_user_corrected)

        if dtype == "phone":
            return cls._validate_phone(clean_val, is_user_corrected)

        if dtype == "date":
            return cls._validate_date(clean_val, is_user_corrected)

        if dtype == "monetary":
            return cls._validate_monetary(clean_val, is_user_corrected)

        if dtype in ("number", "integer"):
            return cls._validate_number(clean_val, dtype, is_user_corrected)

        # Default string handling
        status = "corrected" if is_user_corrected else "valid"
        return ValidationResult(
            is_valid=True,
            status=status,
            normalized_value=clean_val,
            message="Field conforms to string format.",
        )

    @classmethod
    def _validate_email(cls, val: str, is_user_corrected: bool) -> ValidationResult:
        if EMAIL_REGEX.fullmatch(val.strip()):
            normalized = val.strip().lower()
            status = "corrected" if is_user_corrected else "valid"
            return ValidationResult(
                is_valid=True,
                status=status,
                normalized_value=normalized,
                message="Valid email address format.",
            )
        return ValidationResult(
            is_valid=False,
            status="invalid",
            normalized_value=val,
            message="Invalid email syntax (expected name@domain.tld).",
        )

    @classmethod
    def _validate_phone(cls, val: str, is_user_corrected: bool) -> ValidationResult:
        # Strip common formatting characters
        digits = re.sub(r"[^\d+]", "", val)
        raw_digits = re.sub(r"\D", "", val)

        if 7 <= len(raw_digits) <= 15:
            status = "corrected" if is_user_corrected else "valid"
            return ValidationResult(
                is_valid=True,
                status=status,
                normalized_value=digits,
                message="Plausible phone number format.",
            )
        return ValidationResult(
            is_valid=False,
            status="warning",
            normalized_value=val,
            message=f"Phone number length ({len(raw_digits)} digits) is outside expected range (7-15 digits).",
        )

    @classmethod
    def _validate_date(cls, val: str, is_user_corrected: bool) -> ValidationResult:
        try:
            parsed_dt = date_parser.parse(val, fuzzy=True)
            if 1900 <= parsed_dt.year <= 2100:
                normalized = parsed_dt.strftime("%Y-%m-%d")
                status = "corrected" if is_user_corrected else "valid"
                return ValidationResult(
                    is_valid=True,
                    status=status,
                    normalized_value=normalized,
                    message=f"Valid date normalized to ISO-8601 ({normalized}).",
                )
            return ValidationResult(
                is_valid=False,
                status="warning",
                normalized_value=val,
                message=f"Parsed year ({parsed_dt.year}) outside plausible range 1900-2100.",
            )
        except Exception:
            return ValidationResult(
                is_valid=False,
                status="invalid",
                normalized_value=val,
                message="Could not parse date string into a calendar date.",
            )

    @classmethod
    def _validate_monetary(cls, val: str, is_user_corrected: bool) -> ValidationResult:
        # Clean currency symbols and spaces
        cleaned = re.sub(r"[\$€£₹A-Za-z\s]", "", val)
        # Handle comma as thousands separator or decimal separator
        cleaned = cleaned.replace(",", "")
        try:
            amt = float(cleaned)
            normalized = f"{amt:.2f}"
            status = "corrected" if is_user_corrected else "valid"
            return ValidationResult(
                is_valid=True,
                status=status,
                normalized_value=normalized,
                message=f"Monetary amount verified: {normalized}",
            )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                status="invalid",
                normalized_value=val,
                message="Could not parse financial amount as a valid number.",
            )

    @classmethod
    def _validate_number(cls, val: str, dtype: str, is_user_corrected: bool) -> ValidationResult:
        cleaned = val.replace(",", "").strip()
        try:
            if dtype == "integer":
                num = int(cleaned)
                normalized = str(num)
            else:
                num = float(cleaned)
                normalized = str(num)
            status = "corrected" if is_user_corrected else "valid"
            return ValidationResult(
                is_valid=True,
                status=status,
                normalized_value=normalized,
                message=f"Numeric value valid: {normalized}",
            )
        except ValueError:
            return ValidationResult(
                is_valid=False,
                status="invalid",
                normalized_value=val,
                message=f"Value '{val}' is not a valid {dtype}.",
            )
