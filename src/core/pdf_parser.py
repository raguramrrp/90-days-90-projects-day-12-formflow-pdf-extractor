"""PDF validation, text extraction, page rendering, and evidence location."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

from config import (
    MAX_FILE_SIZE_MB,
    MAX_PAGES_LIMIT,
    OCR_DPI,
    SCANNED_PAGE_CHAR_THRESHOLD,
)


@dataclass
class WordBox:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "x0": round(self.x0, 2),
            "top": round(self.top, 2),
            "x1": round(self.x1, 2),
            "bottom": round(self.bottom, 2),
        }


@dataclass
class PageData:
    page_number: int  # 1-indexed
    width: float
    height: float
    text: str
    char_count: int
    word_count: int
    is_scanned_candidate: bool
    words: List[WordBox] = field(default_factory=list)
    ocr_applied: bool = False
    ocr_text: Optional[str] = None


@dataclass
class ExtractedDocumentData:
    file_path: Path
    filename: str
    content_hash: str
    file_size_bytes: int
    page_count: int
    pages: List[PageData]
    metadata: Dict[str, Any]
    is_fully_scanned: bool = False
    validation_error: Optional[str] = None


class PDFParser:
    """Handles PDF file validation, text extraction, word coordinate tracking, and page rendering."""

    def __init__(
        self,
        max_size_mb: int = MAX_FILE_SIZE_MB,
        max_pages: int = MAX_PAGES_LIMIT,
        scanned_threshold: int = SCANNED_PAGE_CHAR_THRESHOLD,
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_pages = max_pages
        self.scanned_threshold = scanned_threshold

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Calculate SHA-256 hash of a file efficiently in 64KB chunks."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validate that the file exists, does not exceed size limits, and has PDF headers."""
        if not file_path.exists():
            return False, f"File does not exist: {file_path.name}"

        size = file_path.stat().st_size
        if size == 0:
            return False, "File is completely empty (0 bytes)."

        if size > self.max_size_bytes:
            mb = size / (1024 * 1024)
            return False, f"File size ({mb:.1f} MB) exceeds maximum allowed limit ({self.max_size_bytes / (1024*1024):.0f} MB)."

        # Check PDF magic bytes (%PDF)
        with open(file_path, "rb") as f:
            header = f.read(8)
            if not header.startswith(b"%PDF"):
                return False, "File is not a valid PDF document (missing %PDF header)."

        return True, None

    def extract_document(self, file_path: Path) -> ExtractedDocumentData:
        """Parse PDF document, extract text per page, collect word bounding boxes, and assess scan status."""
        valid, err = self.validate_file(file_path)
        if not valid:
            raise ValueError(err)

        content_hash = self.calculate_sha256(file_path)
        file_size = file_path.stat().st_size

        import pdfplumber

        pages_data: List[PageData] = []
        doc_metadata: Dict[str, Any] = {}

        try:
            with pdfplumber.open(file_path) as pdf:
                doc_metadata = dict(pdf.metadata) if pdf.metadata else {}
                total_pages = len(pdf.pages)

                if total_pages == 0:
                    raise ValueError("PDF document contains no pages.")

                if total_pages > self.max_pages:
                    raise ValueError(
                        f"PDF page count ({total_pages}) exceeds allowed limit of {self.max_pages} pages."
                    )

                scanned_pages_count = 0

                for idx, page in enumerate(pdf.pages):
                    page_num = idx + 1
                    raw_text = page.extract_text() or ""
                    clean_text = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
                    char_count = len(clean_text)
                    words_extracted = page.extract_words() or []
                    word_boxes = [
                        WordBox(
                            text=w["text"],
                            x0=float(w["x0"]),
                            top=float(w["top"]),
                            x1=float(w["x1"]),
                            bottom=float(w["bottom"]),
                        )
                        for w in words_extracted
                    ]

                    is_scanned = char_count < self.scanned_threshold
                    if is_scanned:
                        scanned_pages_count += 1

                    pages_data.append(
                        PageData(
                            page_number=page_num,
                            width=float(page.width),
                            height=float(page.height),
                            text=clean_text,
                            char_count=char_count,
                            word_count=len(word_boxes),
                            is_scanned_candidate=is_scanned,
                            words=word_boxes,
                        )
                    )

                is_fully_scanned = scanned_pages_count == total_pages

                return ExtractedDocumentData(
                    file_path=file_path,
                    filename=file_path.name,
                    content_hash=content_hash,
                    file_size_bytes=file_size,
                    page_count=total_pages,
                    pages=pages_data,
                    metadata=doc_metadata,
                    is_fully_scanned=is_fully_scanned,
                )

        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            raise RuntimeError(f"Failed to read or parse PDF '{file_path.name}': {exc}") from exc

    @staticmethod
    def render_page_image(file_path: Path, page_number: int = 1, dpi: int = OCR_DPI) -> Image.Image:
        """Render a specific PDF page (1-indexed) into a PIL Image using pypdfium2."""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            import pypdfium2 as pdfium

            pdf = pdfium.PdfDocument(file_path)
            if page_number < 1 or page_number > len(pdf):
                raise IndexError(f"Page {page_number} out of range (1..{len(pdf)}).")

            page = pdf[page_number - 1]
            scale = dpi / 72.0
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()
            return pil_image
        except Exception as exc:
            raise RuntimeError(f"Failed to render page {page_number} for '{file_path.name}': {exc}") from exc
