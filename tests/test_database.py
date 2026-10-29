"""Tests for SQLite persistence, models, relationships, and audit logs."""

from __future__ import annotations

import uuid
import pytest

from src.database.models import DocumentRecord, ExtractedFieldRecord, now_utc_iso


class TestDatabase:
    def test_document_lifecycle(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        doc_id = str(uuid.uuid4())
        doc = DocumentRecord(
            id=doc_id,
            filename="contract.pdf",
            content_hash="abc123hash",
            file_size=10240,
            page_count=2,
            mime_type="application/pdf",
            file_path="data/storage/contract.pdf",
            upload_time=now_utc_iso(),
            processing_status="processing",
            selected_template="General Form",
        )
        doc_repo.insert(doc)

        retrieved = doc_repo.get_by_id(doc_id)
        assert retrieved is not None
        assert retrieved.filename == "contract.pdf"
        assert retrieved.content_hash == "abc123hash"

        # Update status
        doc_repo.update_status(doc_id, "completed", method_summary="Pages: 2, Fields: 5", completed=True)
        updated = doc_repo.get_by_id(doc_id)
        assert updated.processing_status == "completed"
        assert updated.completed_time is not None

    def test_fields_cascade_and_query(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        field_repo = test_repos["field_repo"]

        doc_id = str(uuid.uuid4())
        doc = DocumentRecord(
            id=doc_id,
            filename="test.pdf",
            content_hash="hash99",
            file_size=500,
            page_count=1,
            mime_type="application/pdf",
            file_path="data/test.pdf",
            upload_time=now_utc_iso(),
            processing_status="completed",
        )
        doc_repo.insert(doc)

        f1 = ExtractedFieldRecord(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            field_name="email",
            extracted_value="test@example.com",
            normalized_value="test@example.com",
            data_type="email",
            source_page=1,
            evidence_excerpt="Email: test@example.com",
            bounding_box=None,
            extraction_method="regex",
            validation_status="valid",
            review_status="pending",
            is_user_corrected=0,
            confidence_note="OK",
            created_at=now_utc_iso(),
            updated_at=now_utc_iso(),
        )
        field_repo.insert_batch([f1])

        fields = field_repo.get_by_document(doc_id)
        assert len(fields) == 1
        assert fields[0].field_name == "email"

        # Test field update
        field_repo.update_field(
            field_id=f1.id,
            value="updated@example.com",
            normalized_value="updated@example.com",
            validation_status="valid",
            review_status="verified",
            is_user_corrected=True,
        )
        f_updated = field_repo.get_by_id(f1.id)
        assert f_updated.extracted_value == "updated@example.com"
        assert f_updated.review_status == "verified"
        assert f_updated.is_user_corrected == 1

        # Delete document and verify cascade
        doc_repo.delete(doc_id)
        assert doc_repo.get_by_id(doc_id) is None
        assert field_repo.get_by_document(doc_id) == []

    def test_search_and_filtering(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        for i in range(3):
            doc_repo.insert(
                DocumentRecord(
                    id=str(uuid.uuid4()),
                    filename=f"invoice_{i}.pdf",
                    content_hash=f"hash_{i}",
                    file_size=1000 + i,
                    page_count=1,
                    mime_type="application/pdf",
                    file_path=f"path_{i}",
                    upload_time=now_utc_iso(),
                    processing_status="completed" if i < 2 else "review_required",
                    selected_template="Invoices & Receipts",
                )
            )

        completed = doc_repo.list_all(status_filter="completed")
        assert len(completed) == 2

        search_res = doc_repo.list_all(search_query="invoice_1")
        assert len(search_res) == 1
        assert search_res[0].filename == "invoice_1.pdf"

    def test_audit_log_recording(self, test_repos):
        doc_repo = test_repos["doc_repo"]
        audit_repo = test_repos["audit_repo"]
        doc_id = str(uuid.uuid4())
        doc_repo.insert(
            DocumentRecord(
                id=doc_id,
                filename="audit_sample.pdf",
                content_hash="audit_hash_123",
                file_size=1024,
                page_count=1,
                mime_type="application/pdf",
                file_path="data/audit.pdf",
                upload_time=now_utc_iso(),
                processing_status="completed",
            )
        )
        audit_repo.log(
            document_id=doc_id,
            field_id="f-123",
            field_name="total_amount",
            action="corrected",
            old_value="$100.00",
            new_value="$150.00",
            note="User correction",
        )
        logs = audit_repo.get_by_document(doc_id)
        assert len(logs) == 1
        assert logs[0]["action"] == "corrected"
        assert logs[0]["new_value"] == "$150.00"
