# FormFlow — User Guide

FormFlow is designed to be self-explanatory, productive, and accessible. This user guide covers all primary workflows from document upload to final data export.

---

## 1. Application Navigation
Use the left sidebar radio navigation to access the 6 core workspaces:
1. **Workspace:** Upload launcher, system diagnostics banner, real SQLite metric cards, and quick sample loaders.
2. **Extract & Review:** The central Three-Pane document workstation for visual evidence verification and field editing.
3. **Documents & History:** Searchable and filterable archive of all historical extractions.
4. **Templates & Rules:** Reusable schema manager and interactive regex playground.
5. **Export Center:** Structured JSON and formula-sanitized CSV export generator with live previews.
6. **Settings & Privacy:** Theme toggle (Light/Dark), Tesseract OCR path configuration, and local privacy guarantees.

---

## 2. Ingesting Documents (Workspace Page)
1. Navigate to **Workspace**.
2. **Option A — Upload Your Own PDF:**
   - Drag and drop any `.pdf` document up to 25 MB into the uploader.
   - Choose a matching **Extraction Template** (e.g., *Invoices & Receipts* or *General Form*).
   - Optional: Check *Force OCR on all pages* if you know the document is low-quality or scanned.
   - Click **Process Document**.
3. **Option B — Instant Synthetic Demo:**
   - Click any button in the *Quick-Load Safe Sample Documents* column (e.g., **Load Invoice** or **Load Scanned**).

---

## 3. Reviewing in the Three-Pane Workstation
The **Extract & Review** page is organized into three balanced columns:

### Left Pane: Document Queue
- Displays all currently ingested documents in your session.
- Each item shows the filename, page count, extracted field count, validation warning badges, and processing status.
- Click **Select** on any document card to switch the active workstation focus.
- Click **✕** to remove a document from your active screen queue without deleting its underlying SQLite record.

### Center Pane: PDF Viewer & Source Evidence
- **Visual Preview:** High-resolution page rendering rendered via C++ PDFium.
- **Page Navigation:** Use `◀ Prev` and `Next ▶` buttons to navigate multi-page forms.
- **Evidence Location:** Inspect the exact text snippet and bounding box coordinates (`x0, top, x1, bottom`) mapped to the current page.
- **Extracted Text Tab:** View raw selectable or OCR extracted text for deep inspection.

### Right Pane: Extracted Field Inspector
- Lists all candidate fields detected for the active document.
- **Validation Badges:**
  - `Valid` (Green): Value matches expected data type and formats.
  - `Warning` (Yellow): Value requires human attention (e.g., suspicious phone length).
  - `Missing` (Gray): Required field was not found in the document.
  - `Invalid` (Red): Value violated syntax rules.
  - `Corrected` (Purple): Value was manually edited by a user.
- **Actions per Field:**
  - **Edit Field Value:** Type in the input box and click **Save & Validate** to update the normalized value and record an audit entry.
  - **Verify Field:** Click **Verify Field** to mark the field as human-approved.
  - **Delete Field:** Click the trash icon to remove false positive candidates.
- **Add Custom Field:** Expand the *Add Custom Field to Document* widget to define user-specified fields on the fly.
- **Reprocess:** Expand *Reprocess Document* to re-run extraction with a different template or force OCR.

---

## 4. Searching History (Documents & History)
1. Use the **Search Filename** input to filter documents by name or UUID.
2. Filter by status (`completed`, `review_required`, `failed`) or template category.
3. Click **Review** on any historical row to reopen it in the Three-Pane workstation.
4. Click **Inspect** to review all stored fields and the complete timestamped audit trail.
5. To permanently delete a document, check the confirmation box and click **Delete Permanently**.

---

## 5. Managing Templates & Rules
1. In **Templates & Rules**, select any template (*General Form*, *Invoices & Receipts*, *Application & Registration*, *Business Contracts*) to inspect its field keys, label aliases, and required flags.
2. In the **Create New Template** tab:
   - Provide a Template Name, Category, and Description.
   - Add field keys, data types (`string`, `date`, `monetary`, `email`, `phone`, `number`), and comma-separated aliases.
   - Click **Save Custom Template**.
3. In the **Regex & Rule Tester** tab, enter sample text and test custom regular expressions and anchor labels with instant visual feedback.

---

## 6. Exporting Data (Export Center)
1. Choose **Export Scope**: *Selected Document* or *Batch (All Documents)*.
2. Select **Format**: *JSON* or *CSV*.
3. For CSV, choose between:
   - **Long (Relational):** One row per extracted field with page numbers and evidence excerpts.
   - **Wide (Tabular):** One row per document with column headers for each field.
4. Configure Filters:
   - *Only include Verified fields*
   - *Exclude Invalid / Missing fields*
5. Inspect the live preview window.
6. Click **Download JSON** or **Download CSV** to save the UTF-8 sanitized file.
