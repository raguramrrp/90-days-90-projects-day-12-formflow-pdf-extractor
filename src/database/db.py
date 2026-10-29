"""SQLite Database connection and schema management for FormFlow."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from config import DATABASE_PATH

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    page_count INTEGER NOT NULL,
    mime_type TEXT DEFAULT 'application/pdf',
    file_path TEXT NOT NULL,
    upload_time TEXT NOT NULL,
    processing_status TEXT NOT NULL,
    selected_template TEXT,
    extraction_method_summary TEXT,
    error_message TEXT,
    completed_time TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_upload ON documents(upload_time);

CREATE TABLE IF NOT EXISTS extracted_fields (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    extracted_value TEXT,
    normalized_value TEXT,
    data_type TEXT NOT NULL DEFAULT 'string',
    source_page INTEGER NOT NULL DEFAULT 1,
    evidence_excerpt TEXT,
    bounding_box TEXT,
    extraction_method TEXT NOT NULL,
    validation_status TEXT NOT NULL DEFAULT 'unverified',
    review_status TEXT NOT NULL DEFAULT 'pending',
    is_user_corrected INTEGER NOT NULL DEFAULT 0,
    confidence_note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fields_doc ON extracted_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_fields_name ON extracted_fields(field_name);
CREATE INDEX IF NOT EXISTS idx_fields_val_status ON extracted_fields(validation_status);

CREATE TABLE IF NOT EXISTS templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    rules_json TEXT NOT NULL,
    is_builtin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    field_id TEXT,
    field_name TEXT NOT NULL,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    note TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_doc ON audit_logs(document_id);
"""


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection with row factories."""
    target_path = Path(db_path) if db_path else DATABASE_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize database schema safely without dropping existing tables."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
