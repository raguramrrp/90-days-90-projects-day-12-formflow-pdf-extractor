# FormFlow — 90-Second Demo & Presentation Script

This script is designed for portfolio interviews, recruiter showcases, and hackathon demos to highlight real engineering, clean UI/UX, and architectural depth in under 2 minutes.

---

## ⏱️ Timeline & Talking Points

### 00:00 – 00:20: The Hook & Problem Statement
> *"Hi everyone, today I'm demonstrating **FormFlow**, an Intelligent PDF Form Field Extraction Pipeline built for Day 12 of my 90 Days — 90 Projects Challenge.*
>
> *Students, small businesses, and operations teams routinely receive invoices, applications, and scanned forms. Manual entry is error-prone, but full-blown cloud document AI services require paid API keys, vendor lock-in, and compromise privacy. FormFlow solves this by running 100% locally with deterministic context matching, OCR fallback, human review, and formula-safe structured exports."*

### 00:20 – 00:45: Ingestion & Three-Pane Workstation
> *(Action: Click **Load Invoice** on the Workspace page)*
>
> *"Here on the Workspace dashboard, we have real SQLite-backed metrics and immediate sample ingestion. Let's load a business invoice.*
>
> *This brings us directly into our **Three-Pane Review Workstation**:*
> - *On the **Left Pane**, we have the active document queue showing file size, page count, and status pills.*
> - *In the **Center Pane**, we render the actual PDF page image using the C++ PDFium engine at 160 DPI. We can navigate pages, toggle between the visual document, inspect bounding box coordinates, or view raw text.*
> - *On the **Right Pane**, our Extracted Field Inspector surfaces every detected key: invoice number, date, vendor, customer, line items, and totals."*

### 00:45 – 01:10: Validation, Human Review & Audit Trail
> *(Action: Edit a field value in the right pane and click **Save & Validate**)*
>
> *"Notice the validation pills: valid, warning, missing, or unverified. Our engine doesn't just guess—it normalizes dates to ISO-8601, validates phone plausible lengths, and sanitizes currency tokens.*
>
> *If a user corrects a value, FormFlow instantly re-validates the field, marks it as **Corrected**, and creates an immutable row in SQLite's audit log tracking the timestamp, previous value, and new value."*

### 01:10 – 01:30: Real Scanned Document OCR & Export Safeguards
> *(Action: Switch to Workspace, click **Load Scanned**, show OCR triggered)*
>
> *"What about scanned documents with zero digital text? FormFlow's parser detects character count thresholds below 45 characters, flags the page as a scan candidate, and executes **Tesseract OCR v5.4** directly to extract values like receipt numbers and prices.*
>
> *Finally, over in the **Export Center**, we can preview and download documented JSON or sanitized CSV. We explicitly implement formula injection mitigation: any string starting with `=`, `+`, `-`, or `@` is safely escaped so spreadsheets don't execute dangerous macros."*

### 01:30 – 01:40: Architecture & Wrap-Up
> *"FormFlow is completely tested with **40 automated pytest tests** covering PDF parsing, OCR, regex ranking, SQLite foreign keys, and exporter security. Everything is reproducible on Windows with one click. Thank you!"*
