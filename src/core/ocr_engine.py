"""OCR Engine for scanned PDF forms and image-based document pages using Tesseract."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageEnhance, ImageFilter

from config import TESSERACT_EXECUTABLE


class OCREngine:
    """Manages Tesseract OCR extraction with preprocessing and caching."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or TESSERACT_EXECUTABLE
        self._cache: Dict[Tuple[str, int], str] = {}
        if self.tesseract_cmd:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            except Exception:
                pass

    def is_available(self) -> Tuple[bool, str]:
        """Check if Tesseract binary is detected and operational."""
        if not self.tesseract_cmd or not Path(self.tesseract_cmd).is_file():
            return False, "Tesseract executable not found. Install Tesseract OCR or set TESSERACT_CMD in Settings."

        try:
            import pytesseract
            ver = pytesseract.get_tesseract_version()
            return True, f"Tesseract v{ver} ready."
        except Exception as exc:
            return False, f"Tesseract check failed: {exc}"

    @staticmethod
    def preprocess_image(image: Image.Image) -> Image.Image:
        """Enhance image contrast and sharpness for superior OCR text fidelity."""
        # Convert to grayscale
        gray = image.convert("L")
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)
        # Apply subtle unsharp mask filter to sharpen characters
        sharpened = enhanced.filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=3))
        return sharpened

    def extract_text_from_image(
        self,
        image: Image.Image,
        doc_hash: Optional[str] = None,
        page_num: int = 1,
        lang: str = "eng",
        force_refresh: bool = False,
    ) -> str:
        """Run OCR on a PIL Image, with in-memory caching keyed by doc_hash and page."""
        cache_key = (doc_hash or "adhoc", page_num)
        if not force_refresh and cache_key in self._cache:
            return self._cache[cache_key]

        available, msg = self.is_available()
        if not available:
            raise RuntimeError(f"OCR unavailable: {msg}")

        import pytesseract

        preprocessed = self.preprocess_image(image)

        # Config: psm 6 (assume uniform block of text) or psm 3 (fully automatic page segmentation)
        custom_config = r"--oem 3 --psm 6"

        try:
            raw_text = pytesseract.image_to_string(preprocessed, lang=lang, config=custom_config)
            clean_text = "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())
            self._cache[cache_key] = clean_text
            return clean_text
        except Exception as exc:
            raise RuntimeError(f"Tesseract OCR failed on page {page_num}: {exc}") from exc

    def clear_cache(self) -> None:
        """Clear memory cache of OCR extractions."""
        self._cache.clear()
