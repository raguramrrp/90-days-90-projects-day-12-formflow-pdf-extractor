"""Core processing modules for FormFlow."""

from src.core.pdf_parser import PDFParser, ExtractedDocumentData, PageData
from src.core.ocr_engine import OCREngine
from src.core.field_extractor import FieldExtractor, CandidateField
from src.core.validator import FieldValidator, ValidationResult
from src.core.duplicates import DuplicateDetector

__all__ = [
    "PDFParser",
    "ExtractedDocumentData",
    "PageData",
    "OCREngine",
    "FieldExtractor",
    "CandidateField",
    "FieldValidator",
    "ValidationResult",
    "DuplicateDetector",
]
