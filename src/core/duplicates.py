"""Duplicate detection engine for FormFlow at file and field levels."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.database.models import DocumentRecord, DocumentRepository, ExtractedFieldRecord, FieldRepository


@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    duplicate_type: str  # 'exact_file_hash', 'field_key_match', 'none'
    message: str
    existing_document: Optional[DocumentRecord] = None
    matching_fields: Optional[Dict[str, str]] = None


class DuplicateDetector:
    """Detects document-level hash duplicates and business key field collisions."""

    def __init__(self, doc_repo: DocumentRepository, field_repo: FieldRepository):
        self.doc_repo = doc_repo
        self.field_repo = field_repo

    def check_file_duplicate(self, content_hash: str) -> DuplicateCheckResult:
        """Check if an identical file has previously been processed using SHA-256."""
        existing = self.doc_repo.get_by_hash(content_hash)
        if existing:
            return DuplicateCheckResult(
                is_duplicate=True,
                duplicate_type="exact_file_hash",
                message=f"Identical file already uploaded on {existing.upload_time[:19]} ({existing.filename}).",
                existing_document=existing,
            )
        return DuplicateCheckResult(
            is_duplicate=False,
            duplicate_type="none",
            message="Unique file hash.",
        )

    def check_field_duplicate(
        self,
        current_doc_id: str,
        current_fields: List[ExtractedFieldRecord],
    ) -> List[Dict[str, Any]]:
        """Check for potential business key duplicate collisions across other documents in DB."""
        warnings: List[Dict[str, Any]] = []

        # Find key identifiers like invoice_number, ref_number, application_id
        key_fields: Dict[str, str] = {}
        for f in current_fields:
            if f.field_name in ("invoice_number", "reference_number", "application_id", "registration_id"):
                if f.extracted_value and f.extracted_value.strip():
                    key_fields[f.field_name] = f.extracted_value.strip()

        if not key_fields:
            return warnings

        # Query all documents to check if any other document has matching key fields
        all_docs = self.doc_repo.list_all(limit=500)
        for doc in all_docs:
            if doc.id == current_doc_id:
                continue

            doc_fields = self.field_repo.get_by_document(doc.id)
            for df in doc_fields:
                if df.field_name in key_fields:
                    val = (df.extracted_value or "").strip()
                    target_val = key_fields[df.field_name]
                    if val and val.lower() == target_val.lower():
                        warnings.append(
                            {
                                "field_name": df.field_name,
                                "value": val,
                                "matched_document_id": doc.id,
                                "matched_filename": doc.filename,
                                "upload_time": doc.upload_time,
                                "message": (
                                    f"Field '{df.field_name}' value '{val}' matches existing document "
                                    f"'{doc.filename}' (uploaded {doc.upload_time[:10]})."
                                ),
                            }
                        )

        return warnings
