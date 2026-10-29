# Development Notes & Technical Decisions — FormFlow

## 1. Engineering Decisions & Architecture Trade-offs

### Dual PDF Engine Strategy
- **Issue:** On Windows, many Python PDF rendering libraries (such as `pdf2image`) require external Poppler binaries installed on the system PATH with `pdftoppm.exe`. Requiring Poppler introduces frequent setup failures for non-technical users.
- **Solution:** We selected `pypdfium2`, which bundles Google's native C++ PDFium library in a self-contained wheel. It renders PDF pages to PIL images at arbitrary DPI without external dependencies.
- For text extraction and word-level geometry, we paired it with `pdfplumber` (built on `pdfminer.six`), giving us exact character and word coordinates (`x0, top, x1, bottom`) for visual evidence mapping.

### Local Tesseract Integration & Auto-Discovery
- **Auto-Discovery:** Windows users often install Tesseract to `C:\Program Files\Tesseract-OCR\tesseract.exe` without adding it to their system PATH. FormFlow includes proactive path resolution scanning:
  1. `os.getenv("TESSERACT_CMD")`
  2. `shutil.which("tesseract")`
  3. `C:\Program Files\Tesseract-OCR\tesseract.exe`
  4. `%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe`
- **Graceful Fallback:** If Tesseract is missing, FormFlow displays a non-blocking diagnostic note in the UI and continues processing digital selectable PDFs normally.

### Scanned Document Detection Heuristics
- Rather than running expensive OCR unconditionally on every page (which can take 2-5 seconds per page), FormFlow evaluates the character count of selectable text extracted natively from the page.
- If `char_count < SCANNED_PAGE_CHAR_THRESHOLD` (default 45 characters), the page is classified as a scanned candidate and routed to `OCREngine`.
- Users can also manually force OCR across all pages via a simple checkbox in the UI.

### Candidate Ranking & Alternative Preservation
- A common flaw in simplistic regex extractors is blindly picking the first regex match in a document (e.g., extracting an invoice line item date as the invoice issue date, or extracting a footer email instead of the customer email).
- FormFlow implements deterministic 2-pass candidate scoring:
  - **Pass 1 (Score 100):** Exact label match on the same line (e.g., `Invoice Date: 2026-10-15` or `Email: name@domain.com`).
  - **Pass 2 (Score 50):** Unlabeled regular expression matches across document lines.
- When multiple candidates exist, FormFlow selects the highest-scoring candidate but preserves the alternative values in `ExtractedFieldRecord.confidence_note` so human reviewers can easily switch values.

### SQLite Schema Design & Integrity
- **Durable Persistence:** All document metadata, fields, templates, and audit logs are stored in `data/formflow.db`.
- **WAL Mode:** Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) is enabled on every connection for high-concurrency read operations.
- **Foreign Keys:** Enabled with `PRAGMA foreign_keys = ON;`. Deleting a document in SQLite cascades cleanly to its extracted fields and audit logs.
- **File Separation:** Binary PDF files are not stored as bloated BLOBs in SQLite rows; they are stored in `data/storage/` with UUID-prefixed sanitized names, keeping the database lightweight and fast.

### Formula Injection (CSV / DDE) Mitigation
- When exporting untrusted text fields (such as vendor names, invoice descriptions, or notes) to CSV, spreadsheet software (Excel, Calc, Sheets) will execute formulas if a cell starts with `=`, `+`, `-`, `@`, `\t`, or `\r`.
- FormFlow's `CSVExporter.sanitize_cell()` automatically prefixes any cell starting with these characters with a single apostrophe `'`, neutralizing formula execution while preserving visual legibility.
