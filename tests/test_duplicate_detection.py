"""Tests for Document and Field duplicate detection."""

from __future__ import annotations

import uuid
import pytest

from src.core.duplicates import DuplicateDetector
from src.database.models import DocumentRecord, ExtractedFieldRecord, now_utc_iso


class TestDuplicateDetection:
    def test_file_hash_duplicate_detection(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        field_repo = test_repos["field_repo"]
        detector = DuplicateDetector(doc_repo, field_repo)

        doc1 = DocumentRecord(
            id=str(uuid.uuid4()),
            filename="original.pdf",
            content_hash="sha256_identical_hash_123",
            file_size=2048,
            page_count=1,
            mime_type="application/pdf",
            file_path="data/original.pdf",
            upload_time=now_utc_iso(),
            processing_status="completed",
        )
        doc_repo.insert(doc1)

        # Check duplicate
        res = detector.check_file_duplicate("sha256_identical_hash_123")
        assert res.is_duplicate
        assert res.duplicate_type == "exact_file_hash"
        assert res.existing_document is not None
        assert res.existing_document.filename == "original.pdf"

        # Check unique
        res_unique = detector.check_file_duplicate("different_unique_hash_999")
        assert not res_unique.is_duplicate
        assert res_unique.duplicate_type == "none"

    def test_field_level_duplicate_detection(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        field_repo = test_repos["field_repo"]
        detector = DuplicateDetector(doc_repo, field_repo)

        # Existing doc in DB
        doc_a_id = str(uuid.uuid4())
        doc_repo.insert(
            DocumentRecord(
                id=doc_a_id,
                filename="january_invoice.pdf",
                content_hash="hash_a",
                file_size=2000,
                page_count=1,
                mime_type="application/pdf",
                file_path="data/january.pdf",
                upload_time=now_utc_iso(),
                processing_status="completed",
            )
        )
        field_repo.insert_batch(
            [
                ExtractedFieldRecord(
                    id=str(uuid.uuid4()),
                    document_id=doc_a_id,
                    field_name="invoice_number",
                    extracted_value="INV-2026-001",
                    normalized_value="INV-2026-001",
                    data_type="string",
                    source_page=1,
                    evidence_excerpt="Invoice: INV-2026-001",
                    bounding_box=None,
                    extraction_method="regex",
                    validation_status="valid",
                    review_status="verified",
                    is_user_corrected=0,
                    confidence_note="OK",
                    created_at=now_utc_iso(),
                    updated_at=now_utc_iso(),
                )
            ]
        )

        # New incoming doc with same invoice_number
        doc_b_id = str(uuid.uuid4())
        incoming_fields = [
            ExtractedFieldRecord(
                id=str(uuid.uuid4()),
                document_id=doc_b_id,
                field_name="invoice_number",
                extracted_value="INV-2026-001",
                normalized_value="INV-2026-001",
                data_type="string",
                source_page=1,
                evidence_excerpt="Invoice: INV-2026-001",
                bounding_box=None,
                extraction_method="regex",
                validation_status="valid",
                review_status="pending",
                is_user_corrected=0,
                confidence_note="OK",
                created_at=now_utc_iso(),
                updated_at=now_utc_iso(),
            )
        ]

        warnings = detector.check_field_duplicate(doc_b_id, incoming_fields)
        assert len(warnings) == 1
        assert warnings[0]["field_name"] == "invoice_number"
        assert warnings[0]["value"] == "INV-2026-001"
        assert warnings[0]["matched_filename"] == "january_invoice.pdf"
