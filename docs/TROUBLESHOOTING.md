# Troubleshooting & Common Issues — FormFlow

Solutions to common configuration, runtime, and OCR issues on Windows.

---

## 1. Tesseract OCR Not Detected or Offline
- **Symptom:** UI displays `OCR Offline` or `Tesseract check failed`.
- **Cause:** Tesseract is not installed, or its installation path is not in the system PATH or default `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- **Solution:**
  1. Download the Windows installer from [UB-Mannheim Tesseract Releases](https://github.com/UB-Mannheim/tesseract/wiki).
  2. Install to the default directory (`C:\Program Files\Tesseract-OCR`).
  3. If installed to a non-standard path, create a `.env` file in the project root:
     ```ini
     TESSERACT_CMD=D:\CustomPath\Tesseract-OCR\tesseract.exe
     ```
  4. Restart FormFlow via `run.bat`.

---

## 2. File Size or Page Count Limit Exceeded
- **Symptom:** Error message: `File size exceeds maximum allowed limit (25 MB)` or `PDF page count exceeds allowed limit of 50 pages`.
- **Cause:** Defensive resource limits are enforced to protect local machine memory.
- **Solution:** You can customize resource thresholds in your `.env` file:
  ```ini
  MAX_FILE_SIZE_MB=50
  MAX_PAGES_LIMIT=100
  ```

---

## 3. PDF Page Renders Blank or Incomplete
- **Symptom:** The Center Pane shows a blank preview image.
- **Cause:** The PDF may use encrypted streams or non-standard compression that requires rendering fallbacks.
- **Solution:**
  1. Check the **Extracted Text** tab in the Center Pane to see if native text was extracted.
  2. Check the **Evidence Location** tab to see if word coordinates were extracted.
  3. If the page is a photograph or scan, click **Reprocess Document** and check **Force OCR during reprocess**.

---

## 4. Excel Displays Garbled Currency Symbols or Accented Letters
- **Symptom:** Opening the CSV in Microsoft Excel shows `â‚¬` instead of `€`.
- **Cause:** Excel on Windows defaults to local ANSI code pages unless a UTF-8 Byte Order Mark (BOM) is present.
- **Solution:** FormFlow automatically encodes CSV downloads with `utf-8-sig` (UTF-8 with BOM), allowing Microsoft Excel on Windows to automatically display European accents and currency symbols (`€`, `£`, `₹`) correctly without manual import wizards.

---

## 5. Port 8501 Already in Use
- **Symptom:** `Address already in use` error when running `run.bat`.
- **Cause:** Another Streamlit application or background task is occupying port 8501.
- **Solution:**
  1. In PowerShell, find and terminate the occupying process:
     ```powershell
     Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | Select-Object OwningProcess
     ```
  2. Or run on an alternative port:
     ```powershell
     .\.venv\Scripts\streamlit.exe run app.py --server.port 8502
     ```
