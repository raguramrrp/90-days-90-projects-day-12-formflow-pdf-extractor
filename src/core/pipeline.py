"""FormFlow Extraction & Ingestion Pipeline Orchestrator."""

from __future__ import annotations

import re
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import DATA_STORAGE_DIR
from src.core.duplicates import DuplicateCheckResult, DuplicateDetector
from src.core.field_extractor import CandidateField, FieldExtractor
from src.core.ocr_engine import OCREngine
from src.core.pdf_parser import ExtractedDocumentData, PDFParser
from src.core.validator import FieldValidator
from src.database.models import (
    AuditLogRepository,
    DocumentRecord,
    DocumentRepository,
    ExtractedFieldRecord,
    FieldRepository,
    now_utc_iso,
)
from src.templates.manager import TemplateManager


@dataclass
class PipelineResult:
    document: DocumentRecord
    fields: List[ExtractedFieldRecord]
    duplicate_info: DuplicateCheckResult
    field_duplicate_warnings: List[Dict[str, Any]]
    ocr_pages_count: int
    total_pages: int
    is_reused_from_cache: bool = False
    error: Optional[str] = None


class ExtractionPipeline:
    """End-to-end pipeline connecting PDF parsing, OCR, field extraction, validation, and database storage."""

    def __init__(
        self,
        doc_repo: Optional[DocumentRepository] = None,
        field_repo: Optional[FieldRepository] = None,
        template_mgr: Optional[TemplateManager] = None,
        audit_repo: Optional[AuditLogRepository] = None,
    ):
        self.doc_repo = doc_repo or DocumentRepository()
        self.field_repo = field_repo or FieldRepository()
        self.template_mgr = template_mgr or TemplateManager()
        self.audit_repo = audit_repo or AuditLogRepository()
        self.dup_detector = DuplicateDetector(self.doc_repo, self.field_repo)
        self.pdf_parser = PDFParser()
        self.ocr_engine = OCREngine()
        self.field_extractor = FieldExtractor()

    def process_pdf(
        self,
        file_path_or_bytes: Optional[Path | bytes] = None,
        filename: str = "",
        template_name: str = "General Form",
        force_ocr: bool = False,
        reuse_existing: bool = True,
        file_bytes: Optional[bytes] = None,
    ) -> PipelineResult:
        """Process an uploaded PDF through validation, extraction, OCR (if needed), and persistence."""
        if file_path_or_bytes is None and file_bytes is not None:
            file_path_or_bytes = file_bytes
        if file_path_or_bytes is None:
            raise ValueError("file_path_or_bytes or file_bytes must be provided")
        doc_id = str(uuid.uuid4())
        upload_time = now_utc_iso()

        # 1. Save or prepare local file
        sanitized_name = re.sub(r"[^\w\.-]", "_", filename)
        target_path = DATA_STORAGE_DIR / f"{doc_id[:8]}_{sanitized_name}"

        if isinstance(file_path_or_bytes, bytes):
            with open(target_path, "wb") as f:
                f.write(file_path_or_bytes)
        else:
            shutil.copy2(file_path_or_bytes, target_path)

        file_size = target_path.stat().st_size
        content_hash = self.pdf_parser.calculate_sha256(target_path)

        # 2. Check for duplicate upload
        dup_check = self.dup_detector.check_file_duplicate(content_hash)
        if dup_check.is_duplicate and dup_check.existing_document and reuse_existing:
            existing_doc = dup_check.existing_document
            existing_fields = self.field_repo.get_by_document(existing_doc.id)
            # Remove redundant duplicate file from storage
            if target_path.exists():
                try:
                    target_path.unlink()
                except OSError:
                    pass
            return PipelineResult(
                document=existing_doc,
                fields=existing_fields,
                duplicate_info=dup_check,
                field_duplicate_warnings=[],
                ocr_pages_count=0,
                total_pages=existing_doc.page_count,
                is_reused_from_cache=True,
            )

        # 3. Create initial document record in DB
        doc_record = DocumentRecord(
            id=doc_id,
            filename=filename,
            content_hash=content_hash,
            file_size=file_size,
            page_count=0,
            mime_type="application/pdf",
            file_path=str(target_path),
            upload_time=upload_time,
            processing_status="processing",
            selected_template=template_name,
        )
        self.doc_repo.insert(doc_record)

        try:
            # 4. Extract PDF structure and pages
            doc_data = self.pdf_parser.extract_document(target_path)
            doc_record.page_count = doc_data.page_count

            # 5. Check and run OCR if pages are scanned or user requested force_ocr
            ocr_pages_count = 0
            for page in doc_data.pages:
                needs_ocr = force_ocr or page.is_scanned_candidate
                if needs_ocr and self.ocr_engine.is_available()[0]:
                    try:
                        page_img = self.pdf_parser.render_page_image(target_path, page.page_number)
                        ocr_text = self.ocr_engine.extract_text_from_image(
                            page_img, doc_hash=content_hash, page_num=page.page_number
                        )
                        page.ocr_applied = True
                        page.ocr_text = ocr_text
                        ocr_pages_count += 1
                    except Exception:
                        pass

            # 6. Retrieve active template rules
            template = self.template_mgr.get_template(template_name)
            template_rules = template.get("rules", {}) if template else {}

            # 7. Extract fields
            candidates = self.field_extractor.extract_fields(doc_data.pages, template_rules)

            # 8. Validate and normalize extracted fields
            field_records: List[ExtractedFieldRecord] = []
            has_warnings = False
            has_invalid_or_missing_required = False

            rules_dict = template_rules.get("fields", {})

            for c in candidates:
                field_spec = rules_dict.get(c.field_name, {})
                required = field_spec.get("required", False)
                custom_regex = field_spec.get("regex")

                val_result = FieldValidator.validate_field(
                    field_name=c.field_name,
                    value=c.extracted_value,
                    data_type=c.data_type,
                    required=required,
                    custom_regex=custom_regex,
                )

                if val_result.status in ("invalid", "missing") and required:
                    has_invalid_or_missing_required = True
                elif val_result.status == "warning":
                    has_warnings = True

                import json
                bbox_str = json.dumps(c.bounding_box) if c.bounding_box else None

                f_rec = ExtractedFieldRecord(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    field_name=c.field_name,
                    extracted_value=c.extracted_value,
                    normalized_value=val_result.normalized_value,
                    data_type=c.data_type,
                    source_page=c.source_page,
                    evidence_excerpt=c.evidence_excerpt,
                    bounding_box=bbox_str,
                    extraction_method=c.extraction_method,
                    validation_status=val_result.status,
                    review_status="pending",
                    is_user_corrected=0,
                    confidence_note=c.confidence_note,
                    created_at=now_utc_iso(),
                    updated_at=now_utc_iso(),
                )
                field_records.append(f_rec)

            # 9. Persist fields
            self.field_repo.insert_batch(field_records)

            # 10. Check field duplicate collisions across other documents
            field_warnings = self.dup_detector.check_field_duplicate(doc_id, field_records)

            # 11. Determine final status
            if has_invalid_or_missing_required:
                final_status = "review_required"
            elif has_warnings or field_warnings:
                final_status = "completed_with_warnings"
            else:
                final_status = "completed"

            method_summary = f"Pages: {doc_data.page_count} (OCR: {ocr_pages_count}), Fields: {len(field_records)}"
            self.doc_repo.update_status(
                doc_id=doc_id,
                status=final_status,
                method_summary=method_summary,
                completed=True,
                selected_template=template_name,
            )

            # Update in-memory record
            doc_record.processing_status = final_status
            doc_record.extraction_method_summary = method_summary
            doc_record.completed_time = now_utc_iso()

            # Log audit
            self.audit_repo.log(
                document_id=doc_id,
                field_id=None,
                field_name="document",
                action="extracted",
                note=f"Extraction pipeline completed with status '{final_status}'.",
            )

            return PipelineResult(
                document=doc_record,
                fields=field_records,
                duplicate_info=dup_check,
                field_duplicate_warnings=field_warnings,
                ocr_pages_count=ocr_pages_count,
                total_pages=doc_data.page_count,
            )

        except Exception as exc:
            self.doc_repo.update_status(
                doc_id=doc_id,
                status="failed",
                error_message=str(exc),
                completed=True,
            )
            doc_record.processing_status = "failed"
            doc_record.error_message = str(exc)
            return PipelineResult(
                document=doc_record,
                fields=[],
                duplicate_info=dup_check,
                field_duplicate_warnings=[],
                ocr_pages_count=0,
                total_pages=0,
                error=str(exc),
            )

    def reprocess_document(
        self,
        document_id: str,
        template_name: str,
        force_ocr: bool = False,
    ) -> PipelineResult:
        """Reprocess an existing document with a different template or OCR setting."""
        doc = self.doc_repo.get_by_id(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        target_path = Path(doc.file_path)
        if not target_path.exists():
            raise FileNotFoundError(f"Original PDF file '{target_path.name}' is missing on disk.")

        # Clear existing fields for this document
        self.field_repo.delete_by_document(document_id)

        # Reprocess
        doc_data = self.pdf_parser.extract_document(target_path)
        ocr_pages_count = 0
        for page in doc_data.pages:
            needs_ocr = force_ocr or page.is_scanned_candidate
            if needs_ocr and self.ocr_engine.is_available()[0]:
                try:
                    page_img = self.pdf_parser.render_page_image(target_path, page.page_number)
                    ocr_text = self.ocr_engine.extract_text_from_image(
                        page_img, doc_hash=doc.content_hash, page_num=page.page_number
                    )
                    page.ocr_applied = True
                    page.ocr_text = ocr_text
                    ocr_pages_count += 1
                except Exception:
                    pass

        template = self.template_mgr.get_template(template_name)
        template_rules = template.get("rules", {}) if template else {}
        candidates = self.field_extractor.extract_fields(doc_data.pages, template_rules)

        field_records: List[ExtractedFieldRecord] = []
        has_warnings = False
        has_invalid = False
        rules_dict = template_rules.get("fields", {})

        for c in candidates:
            field_spec = rules_dict.get(c.field_name, {})
            required = field_spec.get("required", False)
            val_result = FieldValidator.validate_field(
                field_name=c.field_name,
                value=c.extracted_value,
                data_type=c.data_type,
                required=required,
            )
            if val_result.status in ("invalid", "missing") and required:
                has_invalid = True
            elif val_result.status == "warning":
                has_warnings = True

            import json
            bbox_str = json.dumps(c.bounding_box) if c.bounding_box else None

            f_rec = ExtractedFieldRecord(
                id=str(uuid.uuid4()),
                document_id=document_id,
                field_name=c.field_name,
                extracted_value=c.extracted_value,
                normalized_value=val_result.normalized_value,
                data_type=c.data_type,
                source_page=c.source_page,
                evidence_excerpt=c.evidence_excerpt,
                bounding_box=bbox_str,
                extraction_method=c.extraction_method,
                validation_status=val_result.status,
                review_status="pending",
                is_user_corrected=0,
                confidence_note=c.confidence_note,
                created_at=now_utc_iso(),
                updated_at=now_utc_iso(),
            )
            field_records.append(f_rec)

        self.field_repo.insert_batch(field_records)
        field_warnings = self.dup_detector.check_field_duplicate(document_id, field_records)

        final_status = "review_required" if has_invalid else ("completed_with_warnings" if has_warnings or field_warnings else "completed")
        method_summary = f"Reprocessed Pages: {doc_data.page_count} (OCR: {ocr_pages_count}), Fields: {len(field_records)}"

        self.doc_repo.update_status(
            doc_id=document_id,
            status=final_status,
            method_summary=method_summary,
            completed=True,
            selected_template=template_name,
        )

        doc.processing_status = final_status
        doc.selected_template = template_name
        doc.extraction_method_summary = method_summary

        self.audit_repo.log(
            document_id=document_id,
            field_id=None,
            field_name="document",
            action="reprocessed",
            note=f"Reprocessed with template '{template_name}' and status '{final_status}'.",
        )

        dup_check = DuplicateCheckResult(is_duplicate=False, duplicate_type="none", message="")

        return PipelineResult(
            document=doc,
            fields=field_records,
            duplicate_info=dup_check,
            field_duplicate_warnings=field_warnings,
            ocr_pages_count=ocr_pages_count,
            total_pages=doc_data.page_count,
        )
