"""Data models and repository access layer for FormFlow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from src.database.db import get_connection


def now_utc_iso() -> str:
    """Return current UTC ISO format string."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DocumentRecord:
    id: str
    filename: str
    content_hash: str
    file_size: int
    page_count: int
    mime_type: str
    file_path: str
    upload_time: str
    processing_status: str
    selected_template: Optional[str] = None
    extraction_method_summary: Optional[str] = None
    error_message: Optional[str] = None
    completed_time: Optional[str] = None

    @classmethod
    def from_row(cls, row: Any) -> DocumentRecord:
        return cls(
            id=row["id"],
            filename=row["filename"],
            content_hash=row["content_hash"],
            file_size=row["file_size"],
            page_count=row["page_count"],
            mime_type=row["mime_type"],
            file_path=row["file_path"],
            upload_time=row["upload_time"],
            processing_status=row["processing_status"],
            selected_template=row["selected_template"],
            extraction_method_summary=row["extraction_method_summary"],
            error_message=row["error_message"],
            completed_time=row["completed_time"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractedFieldRecord:
    id: str
    document_id: str
    field_name: str
    extracted_value: Optional[str]
    normalized_value: Optional[str]
    data_type: str
    source_page: int
    evidence_excerpt: Optional[str]
    bounding_box: Optional[str]  # JSON encoded [x0, top, x1, bottom] or dict
    extraction_method: str
    validation_status: str
    review_status: str
    is_user_corrected: int
    confidence_note: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_row(cls, row: Any) -> ExtractedFieldRecord:
        return cls(
            id=row["id"],
            document_id=row["document_id"],
            field_name=row["field_name"],
            extracted_value=row["extracted_value"],
            normalized_value=row["normalized_value"],
            data_type=row["data_type"],
            source_page=row["source_page"],
            evidence_excerpt=row["evidence_excerpt"],
            bounding_box=row["bounding_box"],
            extraction_method=row["extraction_method"],
            validation_status=row["validation_status"],
            review_status=row["review_status"],
            is_user_corrected=row["is_user_corrected"],
            confidence_note=row["confidence_note"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DocumentRepository:
    """Manages SQLite persistence for PDF documents."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path

    def insert(self, doc: DocumentRecord) -> DocumentRecord:
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, filename, content_hash, file_size, page_count,
                    mime_type, file_path, upload_time, processing_status,
                    selected_template, extraction_method_summary, error_message, completed_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.id,
                    doc.filename,
                    doc.content_hash,
                    doc.file_size,
                    doc.page_count,
                    doc.mime_type,
                    doc.file_path,
                    doc.upload_time,
                    doc.processing_status,
                    doc.selected_template,
                    doc.extraction_method_summary,
                    doc.error_message,
                    doc.completed_time,
                ),
            )
            conn.commit()
        return doc

    def get_by_id(self, doc_id: str) -> Optional[DocumentRecord]:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if row:
                return DocumentRecord.from_row(row)
        return None

    def get_by_hash(self, content_hash: str) -> Optional[DocumentRecord]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE content_hash = ? ORDER BY upload_time DESC LIMIT 1",
                (content_hash,),
            ).fetchone()
            if row:
                return DocumentRecord.from_row(row)
        return None

    def list_all(
        self,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        template_filter: Optional[str] = None,
        limit: int = 100,
    ) -> List[DocumentRecord]:
        query = "SELECT * FROM documents WHERE 1=1"
        params: List[Any] = []

        if search_query:
            query += " AND (filename LIKE ? OR id LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term])

        if status_filter and status_filter.lower() != "all":
            query += " AND processing_status = ?"
            params.append(status_filter.lower())

        if template_filter and template_filter.lower() != "all":
            query += " AND selected_template = ?"
            params.append(template_filter)

        query += " ORDER BY upload_time DESC LIMIT ?"
        params.append(limit)

        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [DocumentRecord.from_row(r) for r in rows]

    def update_status(
        self,
        doc_id: str,
        status: str,
        method_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        completed: bool = False,
        selected_template: Optional[str] = None,
    ) -> None:
        completed_time = now_utc_iso() if completed else None
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE documents
                SET processing_status = ?,
                    extraction_method_summary = COALESCE(?, extraction_method_summary),
                    error_message = ?,
                    completed_time = COALESCE(?, completed_time),
                    selected_template = COALESCE(?, selected_template)
                WHERE id = ?
                """,
                (status, method_summary, error_message, completed_time, selected_template, doc_id),
            )
            conn.commit()

    def delete(self, doc_id: str) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, int]:
        with get_connection(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            completed = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE processing_status IN ('completed', 'completed_with_warnings')"
            ).fetchone()[0]
            review_required = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE processing_status = 'review_required'"
            ).fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM documents WHERE processing_status = 'failed'").fetchone()[0]
            return {
                "total": total,
                "completed": completed,
                "review_required": review_required,
                "failed": failed,
            }


class FieldRepository:
    """Manages SQLite persistence for extracted fields and review states."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path

    def insert_batch(self, fields: List[ExtractedFieldRecord]) -> None:
        if not fields:
            return
        with get_connection(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO extracted_fields (
                    id, document_id, field_name, extracted_value, normalized_value,
                    data_type, source_page, evidence_excerpt, bounding_box,
                    extraction_method, validation_status, review_status,
                    is_user_corrected, confidence_note, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        f.id,
                        f.document_id,
                        f.field_name,
                        f.extracted_value,
                        f.normalized_value,
                        f.data_type,
                        f.source_page,
                        f.evidence_excerpt,
                        f.bounding_box,
                        f.extraction_method,
                        f.validation_status,
                        f.review_status,
                        f.is_user_corrected,
                        f.confidence_note,
                        f.created_at,
                        f.updated_at,
                    )
                    for f in fields
                ],
            )
            conn.commit()

    def get_by_document(self, document_id: str) -> List[ExtractedFieldRecord]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM extracted_fields WHERE document_id = ? ORDER BY source_page ASC, field_name ASC",
                (document_id,),
            ).fetchall()
            return [ExtractedFieldRecord.from_row(r) for r in rows]

    def get_by_id(self, field_id: str) -> Optional[ExtractedFieldRecord]:
        with get_connection(self.db_path) as conn:
            row = conn.execute("SELECT * FROM extracted_fields WHERE id = ?", (field_id,)).fetchone()
            if row:
                return ExtractedFieldRecord.from_row(row)
        return None

    def update_field(
        self,
        field_id: str,
        value: Optional[str],
        normalized_value: Optional[str],
        validation_status: str,
        review_status: str,
        is_user_corrected: bool = True,
    ) -> None:
        now = now_utc_iso()
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE extracted_fields
                SET extracted_value = ?,
                    normalized_value = ?,
                    validation_status = ?,
                    review_status = ?,
                    is_user_corrected = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    value,
                    normalized_value,
                    validation_status,
                    review_status,
                    1 if is_user_corrected else 0,
                    now,
                    field_id,
                ),
            )
            conn.commit()

    def delete_by_document(self, document_id: str) -> int:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM extracted_fields WHERE document_id = ?", (document_id,))
            conn.commit()
            return cursor.rowcount

    def delete(self, field_id: str) -> bool:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM extracted_fields WHERE id = ?", (field_id,))
            conn.commit()
            return cursor.rowcount > 0


class TemplateRepository:
    """Manages SQLite persistence for extraction templates."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path

    def insert(
        self,
        name: str,
        description: str,
        category: str,
        rules: Dict[str, Any],
        is_builtin: bool = False,
        template_id: Optional[str] = None,
    ) -> str:
        tid = template_id or str(uuid.uuid4())
        now = now_utc_iso()
        rules_str = json.dumps(rules, ensure_ascii=False)
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO templates (id, name, description, category, rules_json, is_builtin, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description = excluded.description,
                    category = excluded.category,
                    rules_json = excluded.rules_json,
                    updated_at = excluded.updated_at
                """,
                (tid, name, description, category, rules_str, 1 if is_builtin else 0, now, now),
            )
            conn.commit()
        return tid

    def list_all(self) -> List[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM templates ORDER BY is_builtin DESC, name ASC").fetchall()
            results = []
            for r in rows:
                results.append(
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "description": r["description"],
                        "category": r["category"],
                        "rules": json.loads(r["rules_json"]),
                        "is_builtin": bool(r["is_builtin"]),
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"],
                    }
                )
            return results

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            r = conn.execute("SELECT * FROM templates WHERE name = ?", (name,)).fetchone()
            if r:
                return {
                    "id": r["id"],
                    "name": r["name"],
                    "description": r["description"],
                    "category": r["category"],
                    "rules": json.loads(r["rules_json"]),
                    "is_builtin": bool(r["is_builtin"]),
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                }
        return None

    def delete(self, template_id: str) -> bool:
        with get_connection(self.db_path) as conn:
            # Protect builtin templates
            cursor = conn.execute("DELETE FROM templates WHERE id = ? AND is_builtin = 0", (template_id,))
            conn.commit()
            return cursor.rowcount > 0


class AuditLogRepository:
    """Manages audit trails for corrections and verification."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path

    def log(
        self,
        document_id: str,
        field_id: Optional[str],
        field_name: str,
        action: str,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        note: Optional[str] = None,
    ) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (document_id, field_id, field_name, action, old_value, new_value, note, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (document_id, field_id, field_name, action, old_value, new_value, note, now_utc_iso()),
            )
            conn.commit()

    def get_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM audit_logs WHERE document_id = ? ORDER BY id DESC LIMIT 100",
                (document_id,),
            ).fetchall()
            return [dict(r) for r in rows]
