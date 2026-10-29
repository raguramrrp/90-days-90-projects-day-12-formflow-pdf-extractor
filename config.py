"""Application Configuration and Path Management for FormFlow.

Handles environment loading, Tesseract OCR binary auto-discovery,
database paths, file-storage limits, and runtime diagnostics.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Base Directory of FormFlow Day 12 project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env")

# App Metadata
APP_NAME = os.getenv("APP_NAME", "FormFlow")
APP_TITLE = os.getenv("APP_TITLE", "FormFlow: Intelligent PDF Form Field Extraction Pipeline")
APP_VERSION = "1.0.0"
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

# Storage & Database Directories
DATA_DIR = BASE_DIR / "data"
DATA_STORAGE_DIR = DATA_DIR / "storage"
SAMPLE_PDFS_DIR = DATA_DIR / "sample_pdfs"
DATA_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_PDFS_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DEFAULT_DB_PATH = DATA_DIR / "formflow.db"
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))
if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = BASE_DIR / DATABASE_PATH
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Resource & Processing Limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
MAX_PAGES_LIMIT = int(os.getenv("MAX_PAGES_LIMIT", "50"))
OCR_DPI = int(os.getenv("OCR_DPI", "200"))
SCANNED_PAGE_CHAR_THRESHOLD = int(os.getenv("SCANNED_PAGE_CHAR_THRESHOLD", "45"))
ALLOWED_EXTENSIONS = [".pdf"]

# Tesseract Search Paths
COMMON_TESSERACT_PATHS: List[str] = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/opt/homebrew/bin/tesseract",
]


def resolve_tesseract_path() -> Optional[str]:
    """Auto-detect Tesseract OCR executable across env, PATH, and standard directories."""
    # 1. Check explicit environment override
    env_path = os.getenv("TESSERACT_CMD")
    if env_path and Path(env_path).is_file():
        return env_path

    # 2. Check system PATH
    which_path = shutil.which("tesseract")
    if which_path and Path(which_path).is_file():
        return which_path

    # 3. Check known OS install locations
    for candidate_str in COMMON_TESSERACT_PATHS:
        candidate = Path(candidate_str)
        if candidate.is_file():
            return str(candidate)

    return None


TESSERACT_EXECUTABLE = resolve_tesseract_path()
if TESSERACT_EXECUTABLE:
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXECUTABLE
    except Exception:
        pass


def get_system_diagnostics() -> Dict[str, Any]:
    """Return runtime diagnostic information for UI and verification scripts."""
    ocr_available = False
    ocr_version = "Not Detected"
    ocr_error = None

    if TESSERACT_EXECUTABLE:
        try:
            import pytesseract
            ver = pytesseract.get_tesseract_version()
            ocr_version = str(ver)
            ocr_available = True
        except Exception as exc:
            ocr_error = str(exc)
            ocr_version = f"Error: {exc}"
    else:
        ocr_error = "Binary not found in standard directories or PATH."

    pdfplumber_available = False
    try:
        import pdfplumber
        pdfplumber_available = True
    except ImportError:
        pass

    pypdfium2_available = False
    try:
        import pypdfium2
        pypdfium2_available = True
    except ImportError:
        pass

    spacy_available = False
    spacy_model = None
    try:
        import spacy
        spacy_available = True
        try:
            spacy.load("en_core_web_sm")
            spacy_model = "en_core_web_sm (Loaded)"
        except Exception:
            spacy_model = "Model en_core_web_sm not downloaded (Optional)"
    except ImportError:
        spacy_model = "Not installed (Optional)"

    return {
        "app_name": APP_NAME,
        "app_title": APP_TITLE,
        "app_version": APP_VERSION,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "database_path": str(DATABASE_PATH),
        "storage_dir": str(DATA_STORAGE_DIR),
        "tesseract_path": TESSERACT_EXECUTABLE or "Not Configured",
        "ocr_available": ocr_available,
        "ocr_version": ocr_version,
        "ocr_error": ocr_error,
        "pdfplumber_available": pdfplumber_available,
        "pypdfium2_available": pypdfium2_available,
        "spacy_available": spacy_available,
        "spacy_model": spacy_model,
        "max_file_size_mb": MAX_FILE_SIZE_MB,
        "max_pages_limit": MAX_PAGES_LIMIT,
        "scanned_page_char_threshold": SCANNED_PAGE_CHAR_THRESHOLD,
    }
