# FormFlow Dataset & Sample Documents

This folder contains synthetic, safe, and reproducible test PDF documents created specifically for FormFlow (Day 12 of the 90 Days — 90 Projects Challenge).

## Privacy & Ethics Notice
None of these documents contain real personal identifiable information (PII), real financial accounts, or confidential business data. All names, addresses, amounts, and numbers are synthetic and safe for public portfolio demonstration, hackathons, and GitHub publication.

## Sample Files

### 1. `invoice_sample.pdf`
- **Category:** Finance / Invoices & Receipts
- **Target Fields:**
  - `invoice_number`: `INV-2026-8891`
  - `date`: `2026-10-15`
  - `organization`: `Apex Cloud Solutions Inc.`
  - `person_name`: `Sophia Sterling`
  - `email`: `billing@apexcloud.io`
  - `phone`: `+1-555-019-2831`
  - `total_amount`: `$1,569.63`
  - `address`: `450 Innovation Parkway, Suite 300, Austin, TX 78701`
- **Features:** Multi-item table, tax rate calculation, header block without labeled prefix.

### 2. `job_application_sample.pdf`
- **Category:** Applications / Registration
- **Target Fields:**
  - `application_id`: `APP-9021-X`
  - `submission_date`: `2026-10-20`
  - `person_name`: `Marcus Vance`
  - `email`: `marcus.vance@datascience.edu`
  - `phone`: `+1-415-555-8902`
  - `organization`: `Stanford AI Lab`
  - `address`: `742 Evergreen Terrace, Palo Alto, CA 94301`
- **Features:** Standard two-column application form with strict labeled headers.

### 3. `conference_registration_sample.pdf`
- **Category:** Applications / Events
- **Target Fields:**
  - `registration_id`: `REG-2026-4402`
  - `date`: `2026-10-25`
  - `person_name`: `Elena Rostova`
  - `email`: `elena.rostova@techsummit.org`
  - `phone`: `+44-20-7946-0912`
  - `organization`: `International Robotics Consortium`
  - `total_amount`: `$495.00`
  - `address`: `100 Victoria Embankment, London, EC4Y 0DY`
- **Features:** Registration fee amount extraction and international phone format.

### 4. `vendor_contract_sample.pdf`
- **Category:** Business Contracts / Legal
- **Target Fields:**
  - `reference_number`: `REF-CONTRACT-2026-07`
  - `effective_date`: `2026-11-01`
  - `organization` (Party A): `Global Logistics Corp`
  - `person_name` (Party B): `David Chen`
  - `total_amount` (Contract Value): `$45,000.00`
  - `address`: `1200 Harbor Boulevard, Seattle, WA 98104`
- **Features:** 2-page document with page breaks, testing multi-page text aggregation and page boundary tracing.

### 5. `scanned_receipt_sample.pdf`
- **Category:** Scanned Document / OCR Integration
- **Target Fields:**
  - `invoice_number`: `REC-8832`
  - `date`: `2026-10-28`
  - `person_name`: `Alex Rivera`
  - `phone`: `+1-206-555-3390`
  - `total_amount`: `$42.50`
- **Features:** Pure raster image embedded on canvas with **0 digital text characters**. Automatically triggers the Scanned Document Detector and executes Tesseract OCR.

## Regenerating the Data
You can regenerate or reset all synthetic sample PDFs anytime by running:
```powershell
python scripts\generate_sample_data.py
```
