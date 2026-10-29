"""Test suite configuration and fixtures for FormFlow."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Generator
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import SAMPLE_PDFS_DIR
from src.database.db import get_connection, init_db
from src.database.models import (
    AuditLogRepository,
    DocumentRecord,
    DocumentRepository,
    ExtractedFieldRecord,
    FieldRepository,
    TemplateRepository,
    now_utc_iso,
)


@pytest.fixture(scope="session", autouse=True)
def ensure_sample_pdfs():
    """Ensure all synthetic sample PDFs exist before running tests."""
    from scripts.generate_sample_data import generate_all_sample_pdfs
    generate_all_sample_pdfs()


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Provide an isolated temporary SQLite database for each test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_file = Path(f.name)
    init_db(db_file)
    yield db_file
    if db_file.exists():
        try:
            db_file.unlink()
        except OSError:
            pass


@pytest.fixture
def test_repos(temp_db_path: Path):
    """Provide repository instances connected to an isolated test database."""
    doc_repo = DocumentRepository(db_path=temp_db_path)
    field_repo = FieldRepository(db_path=temp_db_path)
    template_repo = TemplateRepository(db_path=temp_db_path)
    audit_repo = AuditLogRepository(db_path=temp_db_path)
    return {
        "doc_repo": doc_repo,
        "field_repo": field_repo,
        "template_repo": template_repo,
        "audit_repo": audit_repo,
        "db_path": temp_db_path,
    }
