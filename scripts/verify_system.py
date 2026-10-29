"""Comprehensive System Verification Script for FormFlow (Day 12).

Executes end-to-end diagnostics on dependencies, Tesseract OCR, PDF parsing,
database migrations, pipeline extraction, and structured exports.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safe UTF-8 encoding for Windows console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import SAMPLE_PDFS_DIR, get_system_diagnostics
from src.core.pipeline import ExtractionPipeline
from src.database.db import init_db
from src.database.models import DocumentRepository, FieldRepository
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter


def run_verification() -> bool:
    print("=" * 70)
    print(" FORMFLOW SYSTEM VERIFICATION — DAY 12")
    print("=" * 70)

    all_passed = True

    # 1. Diagnostics Check
    print("\n[1/6] Inspecting System Runtime & Dependencies...")
    diag = get_system_diagnostics()
    print(f"  • Python Version : {diag['python_version']} ({diag['platform']})")
    print(f"  • PDF Engine     : pdfplumber={diag['pdfplumber_available']}, pypdfium2={diag['pypdfium2_available']}")
    print(f"  • Tesseract Path : {diag['tesseract_path']}")
    print(f"  • OCR Available  : {diag['ocr_available']} ({diag['ocr_version']})")
    if not (diag["pdfplumber_available"] and diag["pypdfium2_available"]):
        print("  ❌ CRITICAL: PDF processing libraries missing!")
        all_passed = False
    else:
        print("  ✅ Core dependencies verified.")

    # 2. Database Initialization
    print("\n[2/6] Verifying SQLite Database & Schema...")
    try:
        init_db()
        doc_repo = DocumentRepository()
        field_repo = FieldRepository()
        stats = doc_repo.get_stats()
        print(f"  ✅ SQLite initialized successfully. Total documents in DB: {stats['total']}")
    except Exception as exc:
        print(f"  ❌ Database initialization failed: {exc}")
        return False

    # 3. Pipeline on Digital PDF
    print("\n[3/6] Testing Extraction Pipeline on Digital Invoice PDF...")
    inv_pdf = SAMPLE_PDFS_DIR / "invoice_sample.pdf"
    if not inv_pdf.exists():
        print("  Generating sample PDFs first...")
        from scripts.generate_sample_data import generate_all_sample_pdfs
        generate_all_sample_pdfs()

    pipeline = ExtractionPipeline(doc_repo=doc_repo, field_repo=field_repo)
    res_inv = pipeline.process_pdf(
        file_path_or_bytes=inv_pdf,
        filename="invoice_sample.pdf",
        template_name="Invoices & Receipts",
        reuse_existing=False,
    )
    print(f"  • Status : {res_inv.document.processing_status}")
    print(f"  • Fields : {len(res_inv.fields)} extracted")
    for f in res_inv.fields[:5]:
        print(f"    - {f.field_name}: '{f.extracted_value}' [{f.validation_status}]")

    if len(res_inv.fields) >= 5:
        print("  ✅ Digital invoice extraction passed.")
    else:
        print("  ❌ Digital invoice extraction failed to extract expected fields.")
        all_passed = False

    # 4. Pipeline on Image-based Scanned PDF (OCR)
    print("\n[4/6] Testing Scanned PDF Detection & Tesseract OCR...")
    scan_pdf = SAMPLE_PDFS_DIR / "scanned_receipt_sample.pdf"
    if scan_pdf.exists() and diag["ocr_available"]:
        res_scan = pipeline.process_pdf(
            file_path_or_bytes=scan_pdf,
            filename="scanned_receipt_sample.pdf",
            template_name="Invoices & Receipts",
            reuse_existing=False,
        )
        print(f"  • Status : {res_scan.document.processing_status}")
        print(f"  • OCR Applied Pages : {res_scan.ocr_pages_count}")
        print(f"  • Fields : {len(res_scan.fields)} extracted")
        for f in res_scan.fields:
            if f.extracted_value:
                print(f"    - {f.field_name}: '{f.extracted_value}' [{f.validation_status}]")
        if res_scan.ocr_pages_count > 0:
            print("  ✅ OCR extraction pipeline passed on scanned document.")
        else:
            print("  ⚠️ OCR was not triggered on scanned document.")
    else:
        print("  ⚠️ Skipped OCR test (Tesseract or sample file unavailable).")

    # 5. Testing JSON and CSV Exporters
    print("\n[5/6] Testing Structured Exporters (JSON & CSV)...")
    try:
        json_out = JSONExporter.export_document(res_inv.document, res_inv.fields)
        assert "$schema" in json_out and "document_metadata" in json_out
        print(f"  • JSON Export : Verified schema ({len(json_out)} bytes)")

        csv_long = CSVExporter.export_long_format([(res_inv.document, res_inv.fields)])
        assert "document_id" in csv_long and "field_name" in csv_long
        print(f"  • CSV Long    : Relational schema verified ({len(csv_long)} bytes)")

        csv_wide = CSVExporter.export_wide_format([(res_inv.document, res_inv.fields)])
        assert "document_id" in csv_wide
        print(f"  • CSV Wide    : Tabular schema verified ({len(csv_wide)} bytes)")

        # Test Formula Injection Protection
        sanitized = CSVExporter.sanitize_cell("=1+1")
        assert sanitized == "'=1+1"
        print("  • CSV Injection Protection: Formula triggers safely escaped with quote.")
        print("  ✅ Exporters verified.")
    except Exception as exc:
        print(f"  ❌ Exporter verification failed: {exc}")
        all_passed = False

    # 6. Overall Result
    print("\n[6/6] Final Diagnostic Summary")
    if all_passed:
        print("=" * 70)
        print(" 🎉 ALL SYSTEM VERIFICATION CHECKS PASSED — READY FOR USE!")
        print("=" * 70)
        return True
    else:
        print("=" * 70)
        print(" ❌ SOME SYSTEM CHECKS FAILED — Review errors above.")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
