# Architecture & System Design — FormFlow

FormFlow follows a clean, modular 3-tier architecture: Presentation Layer (Streamlit), Core Processing & Business Pipeline, and Data Access Layer (SQLite & Local Storage).

---

## 1. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph Presentation_Layer["UI Presentation Layer (Streamlit)"]
        UI_Workspace["Workspace Dashboard"]
        UI_ThreePane["Three-Pane Workstation (Extract & Review)"]
        UI_History["Documents & History"]
        UI_Templates["Templates & Rules"]
        UI_Export["Export Center (JSON / CSV)"]
        UI_Settings["Settings & Diagnostics"]
    end

    subgraph Core_Pipeline["Core Processing & Extraction Pipeline"]
        Orchestrator["Extraction Pipeline Orchestrator"]
        PDFParser["PDF Parser (pdfplumber + pypdfium2)"]
        ScanDetect["Scanned Page Detector (Heuristics)"]
        OCREngine["Tesseract OCR Engine v5.4"]
        FieldExtractor["Hybrid Field Extractor (Anchors + Regex)"]
        Validator["Validation & Normalization Engine"]
        DupDetector["Duplicate Detector (SHA-256 + Field Key)"]
    end

    subgraph Data_Layer["Durable Local Storage (SQLite & FS)"]
        DB_Docs[("documents Table")]
        DB_Fields[("extracted_fields Table")]
        DB_Templates[("templates Table")]
        DB_Audit[("audit_logs Table")]
        FS_Storage["data/storage/ (UUID Sanitized PDFs)"]
    end

    %% Flows
    UI_Workspace -->|Upload PDF / Choose Template| Orchestrator
    Orchestrator --> PDFParser
    PDFParser -->|Page Rendering & Text Coordinates| ScanDetect
    ScanDetect -->|Char Count < Threshold| OCREngine
    ScanDetect -->|Selectable Text| FieldExtractor
    OCREngine -->|OCR Text| FieldExtractor
    FieldExtractor --> Validator
    Validator --> DupDetector
    DupDetector --> Orchestrator
    
    Orchestrator --> DB_Docs
    Orchestrator --> DB_Fields
    Orchestrator --> FS_Storage
    
    UI_ThreePane <-->|Review, Edit & Verify| DB_Fields
    UI_ThreePane -->|Audit Entry| DB_Audit
    UI_Templates <-->|Save / Retrieve Rules| DB_Templates
    UI_Export -->|Sanitized JSON / CSV| UI_Workspace
```

---

## 2. Extraction Pipeline Execution Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit UI
    participant Pipe as ExtractionPipeline
    participant Parser as PDFParser
    participant OCR as OCREngine
    participant Ext as FieldExtractor
    participant Val as FieldValidator
    participant DB as SQLite Database

    User->>UI: Upload PDF + Select Template
    UI->>Pipe: process_pdf(bytes, filename, template)
    Pipe->>Parser: validate_file() & calculate_sha256()
    alt File Hash already exists
        Pipe->>UI: Return existing record (Offer Cache Reuse)
    else Unique File
        Pipe->>DB: INSERT into documents (status='processing')
        Pipe->>Parser: extract_document()
        loop For each Page
            alt Character Count < Threshold (Scanned)
                Parser->>OCR: render_page_image()
                OCR->>OCR: image_to_string()
            end
        end
        Pipe->>Ext: extract_fields(pages, template_rules)
        loop For each Candidate Field
            Ext->>Val: validate_field(type, value, required)
            Val-->>Ext: ValidationResult(status, normalized_value)
        end
        Pipe->>DB: INSERT into extracted_fields
        Pipe->>DB: UPDATE documents (status='completed' or 'review_required')
        Pipe-->>UI: PipelineResult
        UI-->>User: Display in Three-Pane Workstation
    end
```

---

## 3. Database Schema (Entity Relationship Diagram)

```mermaid
erDiagram
    documents ||--o{ extracted_fields : "contains"
    documents ||--o{ audit_logs : "records"
    templates ||--o{ documents : "guides"

    documents {
        text id PK
        text filename
        text content_hash
        integer file_size
        integer page_count
        text mime_type
        text file_path
        text upload_time
        text processing_status
        text selected_template
        text extraction_method_summary
        text error_message
        text completed_time
    }

    extracted_fields {
        text id PK
        text document_id FK
        text field_name
        text extracted_value
        text normalized_value
        text data_type
        integer source_page
        text evidence_excerpt
        text bounding_box
        text extraction_method
        text validation_status
        text review_status
        integer is_user_corrected
        text confidence_note
        text created_at
        text updated_at
    }

    templates {
        text id PK
        text name UK
        text description
        text category
        text rules_json
        integer is_builtin
        text created_at
        text updated_at
    }

    audit_logs {
        integer id PK
        text document_id FK
        text field_id
        text field_name
        text action
        text old_value
        text new_value
        text note
        text timestamp
    }
```

---

## 4. Key Architectural Decisions

1. **Dual PDF Engine Approach (`pdfplumber` + `pypdfium2`):**
   - `pdfplumber` parses words and exact bounding box coordinates `[x0, top, x1, bottom]`.
   - `pypdfium2` is Google's C++ PDFium renderer in Python, providing blazing-fast page-to-image rasterization at 160 DPI without requiring Poppler binaries on Windows.
2. **Deterministic-First Extraction:**
   - Rather than unpredictable stochastic prompts, FormFlow employs context label anchors (`Invoice Number:`, `Date:`, `Total:`, `Bill To:`) followed by strict regex validation.
3. **SQLite with WAL Mode (`journal_mode = WAL`):**
   - Enables concurrent reads during background extraction without table locks.
   - Foreign key constraints are explicitly enforced (`PRAGMA foreign_keys = ON;`).
4. **Security & Injection Mitigation:**
   - Formula injection mitigation sanitizes spreadsheet cells starting with `=`, `+`, `-`, `@`.
   - Isolated file storage with UUID prefixes prevents filesystem path traversal attacks.
