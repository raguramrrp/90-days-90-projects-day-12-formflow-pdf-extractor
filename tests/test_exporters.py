"""Tests for JSON and CSV Exporters and security protections."""

from __future__ import annotations

import json
import uuid
import pytest

from src.database.models import DocumentRecord, ExtractedFieldRecord, now_utc_iso
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter


@pytest.fixture
def sample_export_data():
    doc_id = str(uuid.uuid4())
    doc = DocumentRecord(
        id=doc_id,
        filename="invoice_march.pdf",
        content_hash="content_hash_12345",
        file_size=15420,
        page_count=1,
        mime_type="application/pdf",
        file_path="data/storage/invoice_march.pdf",
        upload_time=now_utc_iso(),
        processing_status="completed",
        selected_template="Invoices & Receipts",
        extraction_method_summary="Pages: 1, Fields: 3",
        completed_time=now_utc_iso(),
    )
    fields = [
        ExtractedFieldRecord(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            field_name="invoice_number",
            extracted_value="INV-2026-990",
            normalized_value="INV-2026-990",
            data_type="string",
            source_page=1,
            evidence_excerpt="Invoice No: INV-2026-990",
            bounding_box=None,
            extraction_method="context_label",
            validation_status="valid",
            review_status="verified",
            is_user_corrected=0,
            confidence_note="OK",
            created_at=now_utc_iso(),
            updated_at=now_utc_iso(),
        ),
        ExtractedFieldRecord(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            field_name="total_amount",
            extracted_value="€ 2,500.00",
            normalized_value="2500.00",
            data_type="monetary",
            source_page=1,
            evidence_excerpt="Total: € 2,500.00",
            bounding_box=None,
            extraction_method="context_label",
            validation_status="valid",
            review_status="pending",
            is_user_corrected=0,
            confidence_note="OK",
            created_at=now_utc_iso(),
            updated_at=now_utc_iso(),
        ),
        ExtractedFieldRecord(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            field_name="optional_notes",
            extracted_value=None,
            normalized_value=None,
            data_type="string",
            source_page=1,
            evidence_excerpt=None,
            bounding_box=None,
            extraction_method="template_rule",
            validation_status="missing",
            review_status="pending",
            is_user_corrected=0,
            confidence_note=None,
            created_at=now_utc_iso(),
            updated_at=now_utc_iso(),
        ),
    ]
    return doc, fields


class TestExporters:
    def test_json_single_document_export(self, sample_export_data):
        doc, fields = sample_export_data
        json_str = JSONExporter.export_document(doc, fields)
        data = json.loads(json_str)

        assert data["$schema"] == "formflow-v1.0"
        assert data["document_metadata"]["filename"] == "invoice_march.pdf"
        assert len(data["fields"]) == 3

    def test_json_batch_export(self, sample_export_data):
        doc, fields = sample_export_data
        batch_json = JSONExporter.export_batch([(doc, fields)])
        data = json.loads(batch_json)

        assert data["batch_summary"]["total_documents"] == 1
        assert len(data["documents"]) == 1
        assert "invoice_number" in data["documents"][0]["fields"]

    def test_json_filter_verified_only(self, sample_export_data):
        doc, fields = sample_export_data
        json_str = JSONExporter.export_document(doc, fields, only_verified=True)
        data = json.loads(json_str)

        # Only invoice_number was verified
        assert len(data["fields"]) == 1
        assert data["fields"][0]["name"] == "invoice_number"

    def test_csv_long_format_export(self, sample_export_data):
        doc, fields = sample_export_data
        csv_str = CSVExporter.export_long_format([(doc, fields)])

        assert "document_id,filename,upload_time" in csv_str
        assert "INV-2026-990" in csv_str
        assert "invoice_march.pdf" in csv_str

    def test_csv_wide_format_export(self, sample_export_data):
        doc, fields = sample_export_data
        csv_str = CSVExporter.export_wide_format([(doc, fields)])

        lines = csv_str.strip().splitlines()
        header = lines[0]
        assert "invoice_number" in header
        assert "total_amount" in header
        assert len(lines) == 2  # header + 1 document row

    def test_csv_unified_export(self, sample_export_data):
        doc, fields = sample_export_data
        long_str = CSVExporter.export([(doc, fields)], wide_format=False)
        assert "document_id,filename,upload_time" in long_str
        assert "INV-2026-990" in long_str

        wide_str = CSVExporter.export([(doc, fields)], wide_format=True)
        assert "invoice_number" in wide_str
        assert "total_amount" in wide_str

    def test_csv_formula_injection_sanitization(self):
        # Threat payloads
        dangerous_values = ["=cmd|' /C calc'!A0", "+1+1", "-5+2", "@SUM(A1:A10)", "\tmalicious"]
        for val in dangerous_values:
            sanitized = CSVExporter.sanitize_cell(val)
            assert sanitized.startswith("'"), f"Failed to sanitize formula injection for {val}"

        # Safe values should not be modified
        assert CSVExporter.sanitize_cell("Normal Text") == "Normal Text"
        assert CSVExporter.sanitize_cell("12345") == "12345"

    def test_unicode_currency_and_accents_handling(self, sample_export_data):
        doc, fields = sample_export_data
        # total_amount has € currency symbol
        csv_str = CSVExporter.export_long_format([(doc, fields)])
        assert "€" in csv_str
