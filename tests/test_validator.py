"""Tests for Field Validation and Normalization."""

from __future__ import annotations

import pytest

from src.core.validator import FieldValidator


class TestFieldValidator:
    def test_required_field_missing(self):
        res = FieldValidator.validate_field("invoice_number", None, data_type="string", required=True)
        assert not res.is_valid
        assert res.status == "missing"

    def test_optional_field_empty(self):
        res = FieldValidator.validate_field("notes", "", data_type="string", required=False)
        assert res.is_valid
        assert res.status == "unverified"

    def test_valid_email_normalization(self):
        res = FieldValidator.validate_field("email", "USER.NAME@Example.COM", data_type="email")
        assert res.is_valid
        assert res.status == "valid"
        assert res.normalized_value == "user.name@example.com"

    def test_invalid_email_format(self):
        res = FieldValidator.validate_field("email", "not-an-email-address", data_type="email")
        assert not res.is_valid
        assert res.status == "invalid"

    def test_valid_date_normalization(self):
        res = FieldValidator.validate_field("date", "15 October 2026", data_type="date")
        assert res.is_valid
        assert res.status == "valid"
        assert res.normalized_value == "2026-10-15"

    def test_invalid_date(self):
        res = FieldValidator.validate_field("date", "invalid-calendar-date", data_type="date")
        assert not res.is_valid
        assert res.status == "invalid"

    def test_monetary_normalization(self):
        res = FieldValidator.validate_field("total_amount", "$ 1,450.50", data_type="monetary")
        assert res.is_valid
        assert res.status == "valid"
        assert res.normalized_value == "1450.50"

    def test_invalid_monetary(self):
        res = FieldValidator.validate_field("total_amount", "free of charge", data_type="monetary")
        assert not res.is_valid
        assert res.status == "invalid"

    def test_phone_validation(self):
        res = FieldValidator.validate_field("phone", "+1 (555) 019-2831", data_type="phone")
        assert res.is_valid
        assert res.status == "valid"

    def test_user_corrected_status(self):
        res = FieldValidator.validate_field("person_name", "Elena Rostova", data_type="string", is_user_corrected=True)
        assert res.is_valid
        assert res.status == "corrected"

    def test_custom_regex_validation(self):
        res = FieldValidator.validate_field("tax_id", "12-3456789", custom_regex=r"^\d{2}-\d{7}$")
        assert res.is_valid

        res_bad = FieldValidator.validate_field("tax_id", "ABC-123", custom_regex=r"^\d{2}-\d{7}$")
        assert not res_bad.is_valid
        assert res_bad.status == "invalid"
