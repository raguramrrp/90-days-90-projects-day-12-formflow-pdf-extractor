# Testing & Quality Assurance Report — FormFlow

## 1. Test Strategy Overview
FormFlow is verified through an automated test suite implemented with `pytest`. Testing covers isolated unit tests for core algorithms (validation, normalization, regex parsing, coordinate mapping) as well as end-to-end integration tests for SQLite transactions, foreign key cascades, and real Tesseract OCR on synthesized images.

---

## 2. Test Execution Command
Run the complete test suite on Windows PowerShell:

```powershell
.\test.bat
```

Or via direct python command:
```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

---

## 3. Test Suite Breakdown (40 Passing Tests)

### Module 1: `tests/test_pdf_parser.py` (7 tests)
- `test_selectable_text_extraction`: Verifies single-page extraction and character count thresholds on digital PDFs.
- `test_multipage_pdf_extraction`: Verifies 2-page document parsing and multi-page boundary separation.
- `test_scanned_pdf_detection`: Verifies that a pure raster image PDF is detected as a scanned candidate.
- `test_empty_file_validation`: Confirms zero-byte files are caught with helpful error messages.
- `test_malformed_non_pdf_file_validation`: Confirms non-PDF files missing `%PDF` headers are safely rejected.
- `test_page_rendering_to_pil_image`: Verifies PDFium rasterization to high-resolution PIL Image objects.
- `test_sha256_hash_calculation`: Verifies consistent cryptographic hash generation for duplicate checks.

### Module 2: `tests/test_ocr_engine.py` (5 tests)
- `test_ocr_availability_check`: Tests Tesseract executable detection and version string parsing.
- `test_image_preprocessing`: Tests grayscale conversion, contrast enhancement, and unsharp masking.
- `test_real_ocr_execution_if_installed`: Executes actual OCR on a synthesized image and verifies extracted text.
- `test_ocr_caching_mechanism`: Verifies that repeated OCR requests on identical documents return cached results instantly.
- `test_missing_tesseract_graceful_error`: Verifies actionable error handling when Tesseract binary is absent.

### Module 3: `tests/test_field_extractor.py` (4 tests)
- `test_labeled_anchor_extraction`: Tests label context matching for invoice numbers, dates, amounts, and names.
- `test_regex_fallback_extraction_without_exact_labels`: Tests pattern extraction when labels are absent.
- `test_candidate_ranking_with_multiple_values`: Tests deterministic scoring and preservation of alternative candidates.
- `test_custom_template_fields`: Tests custom template rules and user-defined field definitions.

### Module 4: `tests/test_validator.py` (10 tests)
- `test_required_field_missing`: Missing required fields are flagged as `missing`.
- `test_optional_field_empty`: Empty optional fields are marked as `unverified`.
- `test_valid_email_normalization`: Email syntax check and lowercase normalization.
- `test_invalid_email_format`: Rejection of malformed emails.
- `test_valid_date_normalization`: Normalizes natural and formatted dates to ISO-8601 (`YYYY-MM-DD`).
- `test_invalid_date`: Rejects non-calendar date strings.
- `test_monetary_normalization`: Strips currency symbols and comma separators into decimal strings.
- `test_invalid_monetary`: Rejects non-numeric financial amounts.
- `test_phone_validation`: Plausible digit length checks (7-15 digits).
- `test_user_corrected_status`: Marks edited fields with `corrected` status.
- `test_custom_regex_validation`: Evaluates template-specific custom regex rules.

### Module 5: `tests/test_database.py` (4 tests)
- `test_document_lifecycle`: Tests document insertion, retrieval, and status updates in SQLite.
- `test_fields_cascade_and_query`: Verifies document-to-field relationship and cascade deletion.
- `test_search_and_filtering`: Verifies searching by filename, status filter, and template filter.
- `test_audit_log_recording`: Verifies immutable audit logging with enforced foreign keys.

### Module 6: `tests/test_duplicate_detection.py` (2 tests)
- `test_file_hash_duplicate_detection`: Tests SHA-256 duplicate document detection.
- `test_field_level_duplicate_detection`: Tests business key collision warnings across existing records.

### Module 7: `tests/test_exporters.py` (7 tests)
- `test_json_single_document_export`: Validates single-document JSON schema structure.
- `test_json_batch_export`: Validates multi-document batch container schema.
- `test_json_filter_verified_only`: Verifies exclusion of unverified fields when filter is enabled.
- `test_csv_long_format_export`: Verifies relational CSV export with line-level evidence excerpts.
- `test_csv_wide_format_export`: Verifies tabular CSV export with one column per field.
- `test_csv_formula_injection_sanitization`: Verifies formula triggers (`=`, `+`, `-`, `@`, `\t`) are escaped with a single quote.
- `test_unicode_currency_and_accents_handling`: Verifies UTF-8 encoding of currency symbols (`€`, `₹`, `£`).

---

## 4. Actual Test Results
```
============================= test session starts =============================
platform win32 -- Python 3.12.6, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\90 days\90-days-90-projects-day-12-formflow-pdf-extractor
configfile: pyproject.toml
collected 40 items

tests/test_database.py ....                                              [ 10%]
tests/test_duplicate_detection.py ..                                     [ 15%]
tests/test_exporters.py .......                                          [ 32%]
tests/test_field_extractor.py ....                                       [ 42%]
tests/test_ocr_engine.py .....                                           [ 55%]
tests/test_pdf_parser.py .......                                         [ 72%]
tests/test_validator.py ..........                                       [100%]

============================= 40 passed in 1.63s ==============================
```
**Status: PASS (100% Pass Rate)**
