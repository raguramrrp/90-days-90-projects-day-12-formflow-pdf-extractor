"""Tests for OCR Engine and Tesseract integration."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image, ImageDraw

from config import TESSERACT_EXECUTABLE
from src.core.ocr_engine import OCREngine


class TestOCREngine:
    def setup_method(self):
        self.ocr = OCREngine()

    def test_ocr_availability_check(self):
        avail, msg = self.ocr.is_available()
        if TESSERACT_EXECUTABLE and Path(TESSERACT_EXECUTABLE).is_file():
            assert avail
            assert "Tesseract" in msg
        else:
            assert not avail

    def test_image_preprocessing(self):
        img = Image.new("RGB", (200, 100), color=(255, 255, 255))
        preprocessed = self.ocr.preprocess_image(img)
        assert preprocessed.mode == "L"
        assert preprocessed.size == (200, 100)

    def test_real_ocr_execution_if_installed(self):
        avail, _ = self.ocr.is_available()
        if not avail:
            pytest.skip("Tesseract is not installed on this host.")

        # Create a clean image with known text
        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 30), "TEST INVOICE 12345", fill=(0, 0, 0))

        text = self.ocr.extract_text_from_image(img, doc_hash="test_doc", page_num=1)
        assert "TEST" in text or "INVOICE" in text or "12345" in text

    def test_ocr_caching_mechanism(self):
        img = Image.new("RGB", (100, 50), color=(255, 255, 255))
        self.ocr._cache[("mock_doc", 1)] = "CACHED_RESULT_TEXT"

        result = self.ocr.extract_text_from_image(img, doc_hash="mock_doc", page_num=1)
        assert result == "CACHED_RESULT_TEXT"

    def test_missing_tesseract_graceful_error(self):
        bad_ocr = OCREngine(tesseract_cmd=r"C:\NonExistent\tesseract.exe")
        avail, msg = bad_ocr.is_available()
        assert not avail
        assert "not found" in msg.lower()

        img = Image.new("RGB", (50, 50), color=(255, 255, 255))
        with pytest.raises(RuntimeError, match="OCR unavailable"):
            bad_ocr.extract_text_from_image(img)
