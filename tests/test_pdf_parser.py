"""Tests for PDF validation, extraction, and rendering."""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest
from PIL import Image

from config import SAMPLE_PDFS_DIR
from src.core.pdf_parser import PDFParser


class TestPDFParser:
    def setup_method(self):
        self.parser = PDFParser(max_size_mb=25, max_pages=50, scanned_threshold=45)

    def test_selectable_text_extraction(self):
        inv_path = SAMPLE_PDFS_DIR / "invoice_sample.pdf"
        assert inv_path.exists()
        doc = self.parser.extract_document(inv_path)

        assert doc.page_count == 1
        assert not doc.is_fully_scanned
        assert len(doc.pages) == 1
        page = doc.pages[0]
        assert "INV-2026-8891" in page.text
        assert "Sophia Sterling" in page.text
        assert page.char_count > 100
        assert len(page.words) > 20

    def test_multipage_pdf_extraction(self):
        contract_path = SAMPLE_PDFS_DIR / "vendor_contract_sample.pdf"
        assert contract_path.exists()
        doc = self.parser.extract_document(contract_path)

        assert doc.page_count == 2
        assert len(doc.pages) == 2
        assert "MASTER SERVICES AGREEMENT" in doc.pages[0].text
        assert "David Chen" in doc.pages[1].text or "David Chen" in doc.pages[0].text

    def test_scanned_pdf_detection(self):
        scanned_path = SAMPLE_PDFS_DIR / "scanned_receipt_sample.pdf"
        assert scanned_path.exists()
        doc = self.parser.extract_document(scanned_path)

        assert doc.page_count == 1
        assert doc.is_fully_scanned
        assert doc.pages[0].is_scanned_candidate
        assert doc.pages[0].char_count < 45

    def test_empty_file_validation(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = Path(f.name)
        try:
            valid, err = self.parser.validate_file(temp_path)
            assert not valid
            assert "0 bytes" in (err or "")
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_malformed_non_pdf_file_validation(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"This is just plain text, not a real PDF.")
            temp_path = Path(f.name)
        try:
            valid, err = self.parser.validate_file(temp_path)
            assert not valid
            assert "missing %PDF header" in (err or "")
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_page_rendering_to_pil_image(self):
        inv_path = SAMPLE_PDFS_DIR / "invoice_sample.pdf"
        img = self.parser.render_page_image(inv_path, page_number=1, dpi=120)
        assert isinstance(img, Image.Image)
        assert img.width > 500
        assert img.height > 600

    def test_sha256_hash_calculation(self):
        inv_path = SAMPLE_PDFS_DIR / "invoice_sample.pdf"
        hash1 = self.parser.calculate_sha256(inv_path)
        hash2 = self.parser.calculate_sha256(inv_path)
        assert len(hash1) == 64
        assert hash1 == hash2
