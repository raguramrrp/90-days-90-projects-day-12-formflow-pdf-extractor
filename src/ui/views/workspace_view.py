"""Workspace Dashboard View for FormFlow matching the AI reference design."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import streamlit as st

from config import SAMPLE_PDFS_DIR
from src.core.pipeline import ExtractionPipeline
from src.database.models import DocumentRepository
from src.ui.components import get_icon_svg, render_metric_card, render_status_badge, render_top_navigation, safe_html


def render_workspace_view(pipeline: ExtractionPipeline, doc_repo: DocumentRepository) -> None:
    """Render the primary Workspace overview and upload launchpad matching the reference design."""
    # 1. Interactive Top Navigation Bar
    render_top_navigation()

    # 2. Hero Section with 3D Document Illustration (No blank lines inside SVG to prevent Markdown code block leaks)
    doc_header_icon = get_icon_svg("document", color="#2563EB", size=24)
    hero_svg_illustration = """<svg width="130" height="90" viewBox="0 0 130 90" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="70" y="18" width="50" height="46" rx="6" fill="#EFF6FF" stroke="#DBEAFE" stroke-width="1.5"/><rect x="78" y="28" width="22" height="3" rx="1.5" fill="#93C5FD"/><rect x="78" y="36" width="34" height="3" rx="1.5" fill="#BFDBFE"/><rect x="78" y="44" width="28" height="3" rx="1.5" fill="#BFDBFE"/><rect x="24" y="8" width="58" height="70" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/><rect x="30" y="14" width="22" height="10" rx="3" fill="#2563EB"/><text x="34" y="22" fill="#FFFFFF" font-size="7" font-weight="700" font-family="sans-serif">PDF</text><rect x="30" y="32" width="44" height="4" rx="2" fill="#94A3B8"/><rect x="30" y="42" width="34" height="3" rx="1.5" fill="#CBD5E1"/><rect x="30" y="50" width="42" height="3" rx="1.5" fill="#CBD5E1"/><rect x="30" y="58" width="26" height="3" rx="1.5" fill="#CBD5E1"/><circle cx="76" cy="64" r="10" fill="#2563EB"/><path d="M72 64L75 67L80 61" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

    hero_html = f"""
    <div class="ff-hero-container">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box">
                {doc_header_icon}
            </div>
            <div>
                <span class="ff-hero-pill">PDF OCR Pipeline</span>
                <h1 class="ff-hero-title">Workspace Dashboard</h1>
                <p class="ff-hero-subtitle">
                    Upload PDF documents, extract structured business fields, verify evidence, and export validated data.
                </p>
            </div>
        </div>
        <div class="ff-hero-right">
            {hero_svg_illustration}
        </div>
    </div>
    """
    safe_html(hero_html)

    # 3. KPI Metric Cards (Grid of 4)
    stats = doc_repo.get_stats()
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        render_metric_card(
            label="Total Documents",
            value=stats["total"],
            subtext="Stored in local SQLite",
            icon_type="document",
            icon_color="#2563EB",
            icon_bg="#EFF6FF",
        )
    with kpi_col2:
        render_metric_card(
            label="Completed",
            value=stats["completed"],
            subtext="Verified or warning-free",
            icon_type="check_shield",
            icon_color="#059669",
            icon_bg="#ECFDF5",
        )
    with kpi_col3:
        render_metric_card(
            label="Review Required",
            value=stats["review_required"],
            subtext="Missing or invalid fields",
            icon_type="alert_triangle",
            icon_color="#D97706",
            icon_bg="#FFFBEB",
        )
    with kpi_col4:
        render_metric_card(
            label="Failed Jobs",
            value=stats["failed"],
            subtext="Corrupted or blocked",
            icon_type="alert_circle",
            icon_color="#DC2626",
            icon_bg="#FEF2F2",
        )

    # 4. Core Two-Column Layout (Prominent Ingestion on Left, Compact Sample Loaders on Right)
    col_left, col_right = st.columns([1.4, 0.95], gap="medium")

    # =========================================================================
    # LEFT COLUMN: DOCUMENT INGESTION WORKSPACE
    # =========================================================================
    with col_left:
        doc_panel_icon = get_icon_svg("document", color="#2563EB", size=20)
        panel_header_html = f"""
        <div class="ff-panel-header">
            <div class="ff-panel-header-icon">
                {doc_panel_icon}
            </div>
            <div>
                <h3 class="ff-panel-title">Document Ingestion</h3>
                <p class="ff-panel-subtitle">Upload PDF documents and choose an extraction template to start processing.</p>
            </div>
        </div>
        """
        safe_html(panel_header_html)

        uploaded_file = st.file_uploader(
            "Choose a PDF file to process",
            type=["pdf"],
            key="workspace_pdf_uploader",
            label_visibility="collapsed",
        )

        cloud_icon = get_icon_svg("cloud_upload", color="#2563EB", size=22)
        dropzone_html = f"""
        <div class="ff-dropzone">
            <div class="ff-dropzone-cloud">
                {cloud_icon}
            </div>
            <div class="ff-dropzone-text">Drag & drop your PDF file here</div>
            <div class="ff-dropzone-or">or browse from your local disk using the selector above</div>
            <div class="ff-dropzone-info">Supports PDF files • Up to 25MB per file • 100% Local Privacy</div>
        </div>
        """
        safe_html(dropzone_html)

        # Template selection and OCR override
        col_t1, col_t2 = st.columns([1.5, 1.2])
        with col_t1:
            templates = pipeline.template_mgr.list_templates()
            template_options = [t["name"] for t in templates]
            selected_template = st.selectbox(
                "Extraction Template",
                template_options,
                index=0,
                key="workspace_template_select",
            )
        with col_t2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            force_ocr = st.checkbox(
                "Force OCR on all pages",
                value=False,
                key="workspace_force_ocr",
                help="Forces Tesseract OCR on all pages even when selectable text is present.",
            )

        if st.button("Process Document", type="primary", use_container_width=True, disabled=(uploaded_file is None)):
            if uploaded_file is not None:
                with st.spinner("Extracting form fields and validating evidence..."):
                    try:
                        file_bytes = uploaded_file.read()
                        res = pipeline.process_pdf(
                            file_path_or_bytes=file_bytes,
                            filename=uploaded_file.name,
                            template_name=selected_template,
                            force_ocr=force_ocr,
                        )
                        st.session_state["active_doc_id"] = res.document.id
                        st.session_state[f"page_num_{res.document.id}"] = 1
                        st.success(f"Successfully processed '{uploaded_file.name}'!")
                        st.session_state["current_page"] = "Extract & Review"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing document: {e}")

    # =========================================================================
    # RIGHT COLUMN: SLEEK & COMPACT QUICK-LOAD SAMPLE DOCUMENTS
    # =========================================================================
    with col_right:
        lightning_icon = get_icon_svg("lightning", color="#2563EB", size=18)
        sample_header_html = f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <div style="width: 28px; height: 28px; background: var(--ff-accent-light); border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                {lightning_icon}
            </div>
            <h3 style="font-size: 0.98rem; font-weight: 700; color: var(--ff-text-primary); margin: 0;">Quick-Load Safe Samples</h3>
        </div>
        <p style="font-size: 0.76rem; color: var(--ff-text-secondary); margin: 0 0 10px 0;">Test FormFlow with instant synthetic documents.</p>
        """
        safe_html(sample_header_html)

        samples = [
            {
                "key": "invoice",
                "filename": "invoice_sample.pdf",
                "name": "Load Invoice",
                "desc": "Standard business invoice",
                "template": "Invoices & Receipts",
                "icon": "document",
            },
            {
                "key": "job",
                "filename": "job_application_sample.pdf",
                "name": "Load Job App",
                "desc": "Candidate registration form",
                "template": "Application & Registration",
                "icon": "user",
            },
            {
                "key": "conf",
                "filename": "conference_registration_sample.pdf",
                "name": "Load Conference",
                "desc": "Attendee registration form",
                "template": "Application & Registration",
                "icon": "calendar",
            },
            {
                "key": "vendor",
                "filename": "vendor_agreement_sample.pdf",
                "name": "Load Vendor MSA",
                "desc": "2-page Master Services Agreement",
                "template": "Business & Legal Documents",
                "icon": "building",
            },
            {
                "key": "scanned",
                "filename": "scanned_receipt_sample.pdf",
                "name": "Load Scanned",
                "desc": "Scanned receipt (Real OCR)",
                "template": "Invoices & Receipts",
                "icon": "image",
            },
        ]

        for s in samples:
            sample_path = SAMPLE_PDFS_DIR / s["filename"]
            s_icon = get_icon_svg(s["icon"], color="#2563EB", size=16)

            c_info, c_action = st.columns([3.2, 1.1])
            with c_info:
                row_html = f"""
                <div style="display: flex; align-items: center; gap: 8px; padding: 4px 0;">
                    <div style="width: 26px; height: 26px; background: var(--ff-accent-light); border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                        {s_icon}
                    </div>
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 600; color: var(--ff-text-primary); line-height: 1.2;">{s['name']}</div>
                        <div style="font-size: 0.70rem; color: var(--ff-text-secondary);">{s['desc']}</div>
                    </div>
                </div>
                """
                safe_html(row_html)
            with c_action:
                if st.button("Load", key=f"btn_quick_{s['key']}", use_container_width=True):
                    if sample_path.exists():
                        with st.spinner(f"Loading {s['filename']}..."):
                            with open(sample_path, "rb") as f:
                                file_bytes = f.read()
                            res = pipeline.process_pdf(
                                file_path_or_bytes=file_bytes,
                                filename=s["filename"],
                                template_name=s["template"],
                                force_ocr=(s["key"] == "scanned"),
                            )
                            st.session_state["active_doc_id"] = res.document.id
                            st.session_state[f"page_num_{res.document.id}"] = 1
                            st.toast(f"Loaded {s['filename']}!")
                            st.session_state["current_page"] = "Extract & Review"
                            st.rerun()
                    else:
                        st.error(f"Sample file not found at {sample_path}")

    # =========================================================================
    # RECENT PROCESSING HISTORY TABLE
    # =========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    clock_icon = get_icon_svg("history", color="#2563EB", size=18)
    history_header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 28px; height: 28px; background: var(--ff-accent-light); border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                {clock_icon}
            </div>
            <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--ff-text-primary); margin: 0;">Recent Processing History</h3>
        </div>
    </div>
    """
    safe_html(history_header_html)

    recent_docs = doc_repo.list_all(limit=5)
    if not recent_docs:
        st.info("No documents processed yet. Upload a document or load a safe sample above to begin.")
    else:
        for r_doc in recent_docs:
            c_r1, c_r2, c_r3, c_r4, c_r5 = st.columns([3.5, 1.5, 1.2, 1.8, 1.2])
            with c_r1:
                st.markdown(f"**{r_doc.filename}**")
                st.caption(f"ID: `{r_doc.id[:8]}` • {r_doc.upload_time[:19].replace('T', ' ')}")
            with c_r2:
                st.caption(f"Pages: **{r_doc.page_count}**")
                st.caption(f"Template: {r_doc.selected_template or 'None'}")
            with c_r3:
                r_fields = doc_repo.field_repo.get_by_document(r_doc.id) if hasattr(doc_repo, "field_repo") else []
                st.caption(f"Fields: **{len(r_fields)}**")
            with c_r4:
                safe_html(render_status_badge(r_doc.processing_status))
            with c_r5:
                if st.button("Review", key=f"btn_rev_rec_{r_doc.id}", use_container_width=True):
                    st.session_state["active_doc_id"] = r_doc.id
                    st.session_state[f"page_num_{r_doc.id}"] = 1
                    st.session_state["current_page"] = "Extract & Review"
                    st.rerun()
            st.markdown("<hr style='margin: 4px 0 10px 0; border: none; border-top: 1px solid var(--ff-border);'/>", unsafe_allow_html=True)
