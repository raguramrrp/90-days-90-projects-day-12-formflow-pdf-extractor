"""Generate synthetic test PDFs for FormFlow portfolio demonstration.

Creates:
1. invoice_sample.pdf - Standard multi-item invoice
2. job_application_sample.pdf - Candidate registration form
3. conference_registration_sample.pdf - Event attendee registration
4. vendor_contract_sample.pdf - Multi-page business agreement
5. scanned_receipt_sample.pdf - Pure image-based scanned PDF to exercise OCR
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config import SAMPLE_PDFS_DIR


def generate_invoice_sample(output_path: Path) -> Path:
    """Generate a clean business invoice PDF with selectable text."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
    )
    normal_style = ParagraphStyle(
        "InvNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )
    bold_style = ParagraphStyle(
        "InvBold",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # Header
    header_data = [
        [
            Paragraph("<b>Apex Cloud Solutions Inc.</b><br/>100 Tech Blvd, Suite 400<br/>San Francisco, CA 94107<br/>Email: billing@apexcloud.io<br/>Phone: +1-555-019-2831", normal_style),
            Paragraph("<b>INVOICE</b><br/>Invoice Number: <b>INV-2026-8891</b><br/>Date: <b>2026-10-15</b><br/>Due Date: <b>2026-11-15</b>", normal_style),
        ]
    ]
    header_table = Table(header_data, colWidths=[300, 240])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 18))

    # Bill To
    bill_data = [
        [
            Paragraph("<b>Bill To:</b><br/>Customer Name: <b>Sophia Sterling</b><br/>Email: sophia.sterling@enterprise.org<br/>Phone: +1-415-555-0199<br/>Address: 450 Innovation Parkway, Suite 300, Austin, TX 78701", normal_style)
        ]
    ]
    bill_table = Table(bill_data, colWidths=[540])
    bill_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(bill_table)
    story.append(Spacer(1, 18))

    # Line Items
    items_data = [
        ["Description", "Qty", "Unit Price", "Total"],
        ["Enterprise Cloud Platform Subscription (Annual)", "1", "$1,200.00", "$1,200.00"],
        ["Managed Zero-Trust Security Addon", "1", "$250.00", "$250.00"],
        ["", "", "Subtotal:", "$1,450.00"],
        ["", "", "Tax (8.25%):", "$119.63"],
        ["", "", "Total Amount:", "$1,569.63"],
    ]
    items_table = Table(items_data, colWidths=[300, 50, 95, 95])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, 2), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME", (2, 5), (3, 5), "Helvetica-Bold"),
        ("TEXTCOLOR", (2, 5), (3, 5), colors.HexColor("#1e3a8a")),
    ]))
    story.append(items_table)

    doc.build(story)
    return output_path


def generate_application_sample(output_path: Path) -> Path:
    """Generate a job application form PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle("AppNorm", parent=styles["Normal"], fontSize=10, leading=14)

    story = [
        Paragraph("<font size=18><b>Graduate Engineering Fellowship Application</b></font>", normal_style),
        Spacer(1, 12),
        Paragraph("Application ID: <b>APP-9021-X</b>", normal_style),
        Paragraph("Submission Date: <b>2026-10-20</b>", normal_style),
        Spacer(1, 12),
        Paragraph("<b>1. Applicant Details</b>", normal_style),
        Spacer(1, 6),
    ]

    form_data = [
        ["Full Name:", "Marcus Vance"],
        ["Email Address:", "marcus.vance@datascience.edu"],
        ["Phone Number:", "+1-415-555-8902"],
        ["Current Organization:", "Stanford AI Lab"],
        ["Mailing Address:", "742 Evergreen Terrace, Palo Alto, CA 94301"],
    ]
    form_table = Table(form_data, colWidths=[150, 390])
    form_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(form_table)
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>2. Statement of Purpose & Verification</b><br/>I confirm that the above information is accurate and complete.", normal_style))

    doc.build(story)
    return output_path


def generate_registration_sample(output_path: Path) -> Path:
    """Generate an event registration form PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle("RegNorm", parent=styles["Normal"], fontSize=10, leading=14)

    story = [
        Paragraph("<font size=18 color='#1e3a8a'><b>Global AI Summit 2026 — Registration Pass</b></font>", normal_style),
        Spacer(1, 12),
        Paragraph("Registration ID: <b>REG-2026-4402</b>", normal_style),
        Paragraph("Date: <b>2026-10-25</b>", normal_style),
        Spacer(1, 12),
    ]

    reg_data = [
        ["Registrant Name:", "Elena Rostova"],
        ["Contact Email:", "elena.rostova@techsummit.org"],
        ["Contact Phone:", "+44-20-7946-0912"],
        ["Organization:", "International Robotics Consortium"],
        ["Registration Fee:", "$495.00"],
        ["Office Address:", "100 Victoria Embankment, London, EC4Y 0DY"],
    ]
    reg_table = Table(reg_data, colWidths=[150, 390])
    reg_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(reg_table)

    doc.build(story)
    return output_path


def generate_contract_sample(output_path: Path) -> Path:
    """Generate a 2-page Master Services Agreement PDF."""
    from reportlab.platypus import PageBreak

    doc = SimpleDocTemplate(str(output_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle("ContractNorm", parent=styles["Normal"], fontSize=10, leading=14)

    story = [
        Paragraph("<font size=16><b>MASTER SERVICES AGREEMENT</b></font>", normal_style),
        Spacer(1, 10),
        Paragraph("Reference Number: <b>REF-CONTRACT-2026-07</b>", normal_style),
        Paragraph("Effective Date: <b>2026-11-01</b>", normal_style),
        Spacer(1, 12),
        Paragraph("This Agreement is entered into between:", normal_style),
        Paragraph("<b>Party A (Organization):</b> Global Logistics Corp", normal_style),
        Paragraph("Address: 1200 Harbor Boulevard, Seattle, WA 98104", normal_style),
        Spacer(1, 8),
        Paragraph("<b>Party B (Representative):</b> David Chen", normal_style),
        Paragraph("Email: david.chen@globallogistics.com", normal_style),
        Paragraph("Phone: +1-206-555-0144", normal_style),
        Spacer(1, 12),
        Paragraph("<b>Section 1: Scope of Services & Contract Value</b>", normal_style),
        Paragraph("Contract Value: <b>$45,000.00</b> payable in milestone tranches upon verification.", normal_style),
        Spacer(1, 150),
        Paragraph("<i>[Continued on Page 2]</i>", normal_style),
        PageBreak(),
        Paragraph("<font size=14><b>MASTER SERVICES AGREEMENT — PAGE 2</b></font>", normal_style),
        Spacer(1, 12),
        Paragraph("<b>Section 2: Signatures & Execution</b>", normal_style),
        Spacer(1, 10),
        Paragraph("IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the Effective Date.", normal_style),
        Spacer(1, 20),
        Paragraph("Authorized Signatory (Party A): _______________________", normal_style),
        Spacer(1, 15),
        Paragraph("Authorized Signatory (Party B): <b>David Chen</b>", normal_style),
    ]

    doc.build(story)
    return output_path


def generate_scanned_receipt_sample(output_path: Path) -> Path:
    """Generate an image-based PDF (pure raster page with NO digital text) to trigger OCR."""
    from reportlab.pdfgen import canvas

    # 1. Create a raster image with PIL containing receipt text
    img_width, img_height = 800, 1000
    img = Image.new("RGB", (img_width, img_height), color=(250, 250, 248))
    draw = ImageDraw.Draw(img)

    lines = [
        "Cornerstone Cafe & Bistro",
        "742 Market Street, Seattle, WA",
        "Tel: +1-206-555-3390",
        "------------------------------------",
        "RECEIPT NO: REC-8832",
        "Date: 2026-10-28",
        "Customer Name: Alex Rivera",
        "------------------------------------",
        "1x Artisan Espresso        $ 4.50",
        "1x Avocado Sourdough Toast $14.00",
        "1x Truffle Fries           $12.00",
        "1x Sparkling Mineral Water $ 5.00",
        "------------------------------------",
        "Subtotal:                 $35.50",
        "Tax (9.5%):                $ 3.37",
        "Tip:                       $ 3.63",
        "Total Amount:             $42.50",
        "------------------------------------",
        "Thank you for dining with us!",
    ]

    # Draw text lines on the image
    y_pos = 60
    for line in lines:
        draw.text((80, y_pos), line, fill=(20, 25, 30))
        y_pos += 40

    # 2. Embed the raster image into a PDF without adding selectable text
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    from reportlab.lib.utils import ImageReader
    c = canvas.Canvas(str(output_path), pagesize=letter)
    reportlab_img = ImageReader(img_byte_arr)
    c.drawImage(reportlab_img, 0, 0, width=612, height=792)
    c.showPage()
    c.save()

    return output_path


def generate_all_sample_pdfs() -> None:
    """Create all synthetic sample PDFs inside data/sample_pdfs."""
    SAMPLE_PDFS_DIR.mkdir(parents=True, exist_ok=True)

    inv = SAMPLE_PDFS_DIR / "invoice_sample.pdf"
    app = SAMPLE_PDFS_DIR / "job_application_sample.pdf"
    reg = SAMPLE_PDFS_DIR / "conference_registration_sample.pdf"
    con = SAMPLE_PDFS_DIR / "vendor_contract_sample.pdf"
    scan = SAMPLE_PDFS_DIR / "scanned_receipt_sample.pdf"

    print("Generating synthetic sample PDFs...")
    generate_invoice_sample(inv)
    generate_application_sample(app)
    generate_registration_sample(reg)
    generate_contract_sample(con)
    generate_scanned_receipt_sample(scan)
    print(f"All sample PDFs successfully generated in: {SAMPLE_PDFS_DIR}")


if __name__ == "__main__":
    generate_all_sample_pdfs()
