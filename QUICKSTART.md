# FormFlow: Quick Start Guide

Get FormFlow running locally on Windows in under 2 minutes.

---

## ⚡ Method 1: Automated 1-Click Setup (Recommended)

Double-click `setup.bat` or run in PowerShell:

```powershell
.\setup.bat
```

This script automatically:
1. Detects your Python 3.10+ runtime.
2. Creates the dedicated virtual environment `.venv`.
3. Installs all required libraries (`streamlit`, `pdfplumber`, `pypdfium2`, `pytesseract`, `pandas`, `reportlab`, `pytest`).
4. Checks for Tesseract OCR executable.
5. Seeds starter templates and generates synthetic sample PDFs.
6. Runs the full system verification suite.

Then start FormFlow:
```powershell
.\run.bat
```

FormFlow will automatically launch in your browser at `http://localhost:8501`.

---

## 🛠️ Method 2: Manual Setup via PowerShell

If you prefer step-by-step manual configuration:

```powershell
# 1. Navigate to the project directory
cd "D:\90 days\90-days-90-projects-day-12-formflow-pdf-extractor"

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Generate sample PDFs
python scripts\generate_sample_data.py

# 6. Run automated verification
python scripts\verify_system.py

# 7. Start FormFlow
streamlit run app.py
```

---

## 🧪 Running Automated Tests

FormFlow comes with 40 automated tests:

```powershell
.\test.bat
```

Or manually:
```powershell
.\.venv\Scripts\pytest tests -v
```

---

## 🔍 First-Time Demo Sequence

1. Open `http://localhost:8501` in your browser.
2. In the **Workspace** dashboard, click **Load Invoice** under Quick-Load Safe Sample Documents.
3. You will immediately be routed to the **Extract & Review** three-pane workstation:
   - **Left Pane:** View the active document queue.
   - **Center Pane:** Real PDF page image with page navigation and evidence coordinates.
   - **Right Pane:** Editable field inspector with validation pills and audit history.
4. Try editing an amount or name and click **Save & Validate**.
5. Switch to **Export Center** to preview and download structured JSON or sanitized CSV.
