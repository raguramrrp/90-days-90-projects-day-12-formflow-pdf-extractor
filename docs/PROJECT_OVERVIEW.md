# Project Overview — FormFlow

## 1. Problem Statement
Every organization, freelancer, and student deals with recurring PDF forms: vendor invoices, employment applications, membership registrations, receipts, and service agreements. While cloud-based enterprise Document AI solutions exist (e.g., Google Cloud Document AI, AWS Textract), they present serious barriers for local workflows:
- Mandatory credit cards and pay-per-page billing models.
- Cloud vendor lock-in and mandatory internet connectivity.
- Data privacy concerns when transmitting sensitive personal identifiers, financial data, and proprietary contracts to third-party endpoints.
- Brittle mockups that simulate progress indicators without performing genuine OCR or deterministic field extraction.

## 2. Project Vision & Solution
**FormFlow** is an open-source, local-first Intelligent PDF Form Field Extraction Pipeline. Built for Day 12 of the **90 Days — 90 Projects Challenge**, FormFlow bridges deterministic document parsing, local OCR, and human-in-the-loop review within a responsive desktop-grade Streamlit workstation.

FormFlow requires **zero paid APIs**, runs 100% offline on Windows, persists durable metadata in local SQLite with write-ahead logging (WAL), and outputs production-grade JSON and CSV datasets.

## 3. Target Personas & Use Cases
- **Students & Researchers:** Ingesting academic application forms, conference registrations, and survey PDFs without manual transcription.
- **Freelancers & Small Business Owners:** Processing monthly vendor invoices, utility bills, and payment vouchers into structured spreadsheets.
- **HR & Operations Teams:** Reviewing standard employment application forms and cross-referencing contact info, dates, and qualifications.
- **Data Engineers & Analysts:** Creating verified training sets and structured tables from heterogeneous document archives.

## 4. MVP Boundaries & Honest Scope
- **In Scope:**
  - Standard selectable text PDF parsing via `pdfplumber`.
  - Scanned PDF detection and local optical character recognition via `Tesseract OCR v5.4`.
  - C++ PDFium page rendering at 160+ DPI for high-fidelity visual preview.
  - Hybrid extraction combining context label anchors, regular expressions, and configurable template aliases.
  - Human review workstation with editable field cards, live revalidation, and immutable audit logging.
  - Level-1 (SHA-256 hash) and Level-2 (business key) duplicate detection.
  - Structured JSON schema and formula-injection-safe CSV exports.
- **Out of Scope (Explicit Non-Goals):**
  - Full legal contract interpretation or automated legal risk analysis (this is structured extraction, not legal advice).
  - Cloud-synchronized multi-tenant databases.
  - Expensive generative LLM API calls for arbitrary unconstrained document reasoning.

## 5. Privacy, Ethics & Synthetic Data
FormFlow treats all uploaded files as untrusted local input. Documents are stored in an isolated local directory with sanitized UUID filenames. All test PDFs packaged with the application are generated synthetically using `reportlab`, ensuring zero exposure of real personal identifiable information (PII).
