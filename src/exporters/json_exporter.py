"""JSON Exporter with documented schema for single documents and batches."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.database.models import DocumentRecord, ExtractedFieldRecord


class JSONExporter:
    """Exports structured field extractions to validated JSON schemas."""

    SCHEMA_VERSION = "formflow-v1.0"

    @classmethod
    def export_document(
        cls,
        doc: DocumentRecord,
        fields: List[ExtractedFieldRecord],
        only_verified: bool = False,
        exclude_invalid: bool = False,
    ) -> str:
        """Export a single document to standard JSON string."""
        filtered_fields = cls._filter_fields(fields, only_verified, exclude_invalid)

        doc_payload = {
            "$schema": cls.SCHEMA_VERSION,
            "document_metadata": {
                "id": doc.id,
                "filename": doc.filename,
                "content_hash": doc.content_hash,
                "file_size_bytes": doc.file_size,
                "page_count": doc.page_count,
                "upload_time": doc.upload_time,
                "completed_time": doc.completed_time,
                "processing_status": doc.processing_status,
                "template": doc.selected_template,
                "extraction_method_summary": doc.extraction_method_summary,
            },
            "fields_count": len(filtered_fields),
            "fields": [
                {
                    "name": f.field_name,
                    "extracted_value": f.extracted_value,
                    "normalized_value": f.normalized_value,
                    "data_type": f.data_type,
                    "source_page": f.source_page,
                    "evidence_excerpt": f.evidence_excerpt,
                    "extraction_method": f.extraction_method,
                    "validation_status": f.validation_status,
                    "review_status": f.review_status,
                    "is_user_corrected": bool(f.is_user_corrected),
                    "confidence_note": f.confidence_note,
                }
                for f in filtered_fields
            ],
        }

        return json.dumps(doc_payload, indent=2, ensure_ascii=False)

    # Alias for export_document
    export_single = export_document

    @classmethod
    def export_batch(
        cls,
        items: List[tuple[DocumentRecord, List[ExtractedFieldRecord]]],
        only_verified: bool = False,
        exclude_invalid: bool = False,
    ) -> str:
        """Export multiple documents in a single structured JSON batch container."""
        batch_payload = {
            "$schema": cls.SCHEMA_VERSION,
            "batch_summary": {
                "total_documents": len(items),
                "export_filter_verified_only": only_verified,
                "export_filter_exclude_invalid": exclude_invalid,
            },
            "documents": [],
        }

        for doc, fields in items:
            filtered = cls._filter_fields(fields, only_verified, exclude_invalid)
            batch_payload["documents"].append(
                {
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "template": doc.selected_template,
                    "status": doc.processing_status,
                    "fields": {
                        f.field_name: {
                            "value": f.extracted_value,
                            "normalized": f.normalized_value,
                            "data_type": f.data_type,
                            "page": f.source_page,
                            "validation": f.validation_status,
                            "review": f.review_status,
                        }
                        for f in filtered
                    },
                }
            )

        return json.dumps(batch_payload, indent=2, ensure_ascii=False)

    @staticmethod
    def _filter_fields(
        fields: List[ExtractedFieldRecord],
        only_verified: bool,
        exclude_invalid: bool,
    ) -> List[ExtractedFieldRecord]:
        results = []
        for f in fields:
            if only_verified and f.review_status != "verified":
                continue
            if exclude_invalid and f.validation_status in ("invalid", "missing"):
                continue
            results.append(f)
        return results
