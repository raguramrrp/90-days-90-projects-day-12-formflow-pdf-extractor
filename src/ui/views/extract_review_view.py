"""Extract & Review: The Three-Pane Document Review Workstation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

from config import DATA_STORAGE_DIR
from src.core.pdf_parser import PDFParser
from src.core.pipeline import ExtractionPipeline
from src.core.validator import FieldValidator
from src.database.models import (
    AuditLogRepository,
    DocumentRecord,
    DocumentRepository,
    ExtractedFieldRecord,
    FieldRepository,
    now_utc_iso,
)
from src.ui.components import get_icon_svg, render_status_badge, render_top_navigation, safe_html


def render_extract_review_view(
    pipeline: ExtractionPipeline,
    doc_repo: DocumentRepository,
    field_repo: FieldRepository,
    audit_repo: AuditLogRepository,
) -> None:
    """Render the primary Three-Pane Document Review Workstation."""
    render_top_navigation()

    # Section Header
    extract_icon = get_icon_svg("extract", color="#2563EB", size=24)
    header_html = f"""
    <div class="ff-hero-container" style="padding: 16px 22px; margin-bottom: 16px;">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box" style="width: 44px; height: 44px;">
                {extract_icon}
            </div>
            <div>
                <span class="ff-hero-pill">Three-Pane Workstation</span>
                <h2 class="ff-hero-title" style="font-size: 1.35rem; margin: 0 0 2px 0;">Extract & Review Workspace</h2>
                <p class="ff-hero-subtitle" style="font-size: 0.82rem;">
                    Inspect visual page evidence, verify extracted field candidates, and correct values before structured export.
                </p>
            </div>
        </div>
    </div>
    """
    safe_html(header_html)

    all_docs = doc_repo.list_all(limit=100)
    if not all_docs:
        st.info("No documents in the system yet. Please upload or load a sample document from the Workspace page.")
        if st.button("Go to Workspace Dashboard", type="primary"):
            st.session_state["current_page"] = "Workspace"
            st.rerun()
        return

    # Determine Active Document
    active_doc_id = st.session_state.get("active_doc_id")
    if not active_doc_id or not any(d.id == active_doc_id for d in all_docs):
        active_doc_id = all_docs[0].id
        st.session_state["active_doc_id"] = active_doc_id

    active_doc = doc_repo.get_by_id(active_doc_id)
    if not active_doc:
        active_doc = all_docs[0]
        st.session_state["active_doc_id"] = active_doc.id

    # Active Page State for PDF viewer
    page_state_key = f"page_num_{active_doc.id}"
    if page_state_key not in st.session_state:
        st.session_state[page_state_key] = 1

    current_page = st.session_state[page_state_key]
    max_pages = max(1, active_doc.page_count)
    if current_page > max_pages:
        current_page = 1
        st.session_state[page_state_key] = 1

    # THREE-PANE LAYOUT
    col_left, col_center, col_right = st.columns([2.6, 4.4, 5.0], gap="medium")

    # =========================================================================
    # LEFT PANE: DOCUMENT QUEUE
    # =========================================================================
    with col_left:
        queue_header_html = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 1.0rem; font-weight: 700; color: var(--ff-text-primary); margin: 0;">Document Queue</h3>
            <span style="font-size: 0.75rem; background: var(--ff-accent-light); color: var(--ff-accent); font-weight: 600; padding: 2px 8px; border-radius: 12px;">{len(all_docs)} loaded</span>
        </div>
        """
        safe_html(queue_header_html)

        # Quick Upload inside Queue
        with st.expander("Ingest to Queue", expanded=False):
            q_file = st.file_uploader("Upload PDF", type=["pdf"], key="queue_uploader", label_visibility="collapsed")
            q_template = st.selectbox(
                "Template",
                [t["name"] for t in pipeline.template_mgr.list_templates()],
                key="q_template_sel",
            )
            if st.button("Process & Add", key="q_add_btn", disabled=(q_file is None), use_container_width=True):
                if q_file:
                    with st.spinner("Processing..."):
                        res = pipeline.process_pdf(q_file.read(), q_file.name, template_name=q_template)
                        st.session_state["active_doc_id"] = res.document.id
                        st.session_state[f"page_num_{res.document.id}"] = 1
                        st.success(f"Added {res.document.filename}")
                        st.rerun()

        # Document List Items
        for doc in all_docs:
            is_active = (doc.id == active_doc.id)
            doc_fields = field_repo.get_by_document(doc.id)
            warnings_count = sum(1 for f in doc_fields if f.validation_status in ("warning", "invalid", "missing"))

            active_border = "border-left: 4px solid var(--ff-accent); background-color: var(--ff-accent-light); border-color: var(--ff-border);" if is_active else "border: 1px solid var(--ff-border); background-color: var(--ff-bg-card);"
            badge_html = render_status_badge(doc.processing_status)

            doc_card_html = f"""
            <div style="padding: 10px 12px; border-radius: 8px; margin-bottom: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); {active_border}">
                <div style="font-size: 0.85rem; font-weight: 600; color: var(--ff-text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                    {doc.filename}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                    <span style="font-size: 0.72rem; color: var(--ff-text-secondary);">
                        {doc.page_count} pg • {len(doc_fields)} flds {f'• <span style="color:#DC2626; font-weight:600;">{warnings_count} warn</span>' if warnings_count else ''}
                    </span>
                    {badge_html}
                </div>
            </div>
            """
            safe_html(doc_card_html)

            col_btn_sel, col_btn_rem = st.columns([3, 1])
            with col_btn_sel:
                if st.button("Select Focus", key=f"q_sel_{doc.id}", disabled=is_active, use_container_width=True):
                    st.session_state["active_doc_id"] = doc.id
                    st.session_state[f"page_num_{doc.id}"] = 1
                    st.rerun()
            with col_btn_rem:
                if st.button("✕", key=f"q_rem_{doc.id}", help="Remove from active queue (preserves stored SQLite history)"):
                    remaining = [d for d in all_docs if d.id != doc.id]
                    if remaining:
                        st.session_state["active_doc_id"] = remaining[0].id
                    else:
                        st.session_state["active_doc_id"] = None
                    st.rerun()

    # =========================================================================
    # CENTER PANE: PDF VIEWER & SOURCE EVIDENCE
    # =========================================================================
    with col_center:
        viewer_header_html = """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 1.0rem; font-weight: 700; color: var(--ff-text-primary); margin: 0;">PDF Visual Viewer</h3>
        </div>
        """
        safe_html(viewer_header_html)
        doc_file_path = Path(active_doc.file_path)

        # Page Navigation Bar
        nav_prev, nav_info, nav_next = st.columns([1, 2, 1])
        with nav_prev:
            if st.button("◀ Prev", key="btn_prev_page", disabled=(current_page <= 1), use_container_width=True):
                st.session_state[page_state_key] = max(1, current_page - 1)
                st.rerun()
        with nav_info:
            page_info_html = f"""
            <div style="text-align: center; font-size: 0.85rem; font-weight: 600; color: var(--ff-text-primary); padding: 6px 0; background: var(--ff-bg-card); border: 1px solid var(--ff-border); border-radius: 6px;">
                Page {current_page} of {max_pages}
            </div>
            """
            safe_html(page_info_html)
        with nav_next:
            if st.button("Next ▶", key="btn_next_page", disabled=(current_page >= max_pages), use_container_width=True):
                st.session_state[page_state_key] = min(max_pages, current_page + 1)
                st.rerun()

        # Tabs for Preview Options
        tab_img, tab_evidence, tab_text = st.tabs(["Visual Preview", "Evidence Location", "Extracted Text"])

        with tab_img:
            if doc_file_path.exists():
                try:
                    pil_img = PDFParser.render_page_image(doc_file_path, page_number=current_page, dpi=160)
                    st.image(pil_img, use_container_width=True, caption=f"{active_doc.filename} — Page {current_page}")
                except Exception as e:
                    st.error(f"Could not render page image: {e}")
            else:
                st.warning(
                    f"Original PDF file is not present on disk at `{active_doc.file_path}`. "
                    f"Extracted metadata and fields are preserved in SQLite."
                )

        with tab_evidence:
            st.markdown("#### Mapped Evidence Bounding Boxes")
            active_fields = field_repo.get_by_document(active_doc.id)
            page_fields = [f for f in active_fields if f.source_page == current_page]
            if not page_fields:
                st.caption(f"No fields mapped directly to Page {current_page}.")
            else:
                for pf in page_fields:
                    bbox_text = ""
                    if pf.bounding_box:
                        try:
                            bb = json.loads(pf.bounding_box)
                            bbox_text = f"BBox: [x0: {bb.get('x0')}, top: {bb.get('top')}, x1: {bb.get('x1')}, bottom: {bb.get('bottom')}]"
                        except Exception:
                            pass
                    bbox_card_html = f"""
                    <div style="background-color: var(--ff-bg-card); border: 1px solid var(--ff-border); border-radius: 8px; padding: 8px 12px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600; font-size: 0.84rem; color: var(--ff-text-primary);">{pf.field_name}</span>
                            <span style="font-size: 0.70rem; color: var(--ff-accent); background: var(--ff-accent-light); padding: 1px 6px; border-radius: 4px;">{pf.extraction_method}</span>
                        </div>
                        <div style="font-family: monospace; font-size: 0.78rem; color: var(--ff-accent); background: var(--ff-bg-subtle); padding: 4px 8px; border-radius: 4px; margin: 4px 0;">"{pf.evidence_excerpt or pf.extracted_value}"</div>
                        <div style="font-size: 0.70rem; color: var(--ff-text-secondary);">{bbox_text}</div>
                    </div>
                    """
                    safe_html(bbox_card_html)

        with tab_text:
            try:
                doc_data = pipeline.pdf_parser.extract_document(doc_file_path)
                if current_page <= len(doc_data.pages):
                    raw_txt = doc_data.pages[current_page - 1].text
                    st.text_area("Selectable Text", value=raw_txt or "[No selectable text on this page]", height=320)
            except Exception:
                st.caption("Raw text could not be loaded directly from file.")

    # =========================================================================
    # RIGHT PANE: EXTRACTED FIELD INSPECTOR
    # =========================================================================
    with col_right:
        inspector_header_html = """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 1.0rem; font-weight: 700; color: var(--ff-text-primary); margin: 0;">Extracted Field Inspector</h3>
        </div>
        """
        safe_html(inspector_header_html)

        status_badge_html = render_status_badge(active_doc.processing_status)
        doc_summary_html = f"""
        <div style="background-color: var(--ff-bg-card); border: 1px solid var(--ff-border); border-radius: 10px; padding: 12px 14px; margin-bottom: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 0.95rem; color: var(--ff-text-primary);">{active_doc.filename}</span>
                {status_badge_html}
            </div>
            <div style="font-size: 0.76rem; color: var(--ff-text-secondary); margin-top: 4px;">
                Template: <b>{active_doc.selected_template or 'None'}</b> • Uploaded: {active_doc.upload_time[:19].replace('T', ' ')}
            </div>
        </div>
        """
        safe_html(doc_summary_html)

        fields = field_repo.get_by_document(active_doc.id)
        if not fields:
            st.info("No fields extracted for this document. Use the Reprocess controls below to run extraction.")
        else:
            for f in fields:
                with st.container():
                    # Field Header Row
                    col_fh1, col_fh2 = st.columns([3, 2])
                    with col_fh1:
                        f_header_html = f"""
                        <span style="font-size: 0.88rem; font-weight: 600; color: var(--ff-text-primary);">{f.field_name.replace('_', ' ').title()}</span>
                        <span style="font-size: 0.70rem; color: var(--ff-accent); background: var(--ff-accent-light); padding: 2px 6px; border-radius: 4px; font-weight: 500;">{f.data_type}</span>
                        """
                        safe_html(f_header_html)
                    with col_fh2:
                        val_badge = render_status_badge(f.validation_status)
                        rev_badge = render_status_badge(f.review_status)
                        badges_row_html = f"<div style='text-align: right;'>{val_badge} {rev_badge}</div>"
                        safe_html(badges_row_html)

                    # Evidence Excerpt if available
                    if f.evidence_excerpt:
                        excerpt_html = f"""
                        <div style="font-size: 0.74rem; color: var(--ff-text-primary); background: var(--ff-bg-subtle); padding: 4px 8px; border-radius: 4px; margin: 4px 0; border-left: 3px solid var(--ff-accent); font-family: monospace;">
                            Excerpt (Pg {f.source_page}): "{f.evidence_excerpt}"
                        </div>
                        """
                        safe_html(excerpt_html)

                    # Editable Value Input
                    input_key = f"val_input_{f.id}"
                    edited_val = st.text_input(
                        "Extracted Value",
                        value=f.extracted_value or "",
                        key=input_key,
                        label_visibility="collapsed",
                    )

                    # Normalized preview if different
                    if f.normalized_value and f.normalized_value != f.extracted_value:
                        st.caption(f"Normalized: `{f.normalized_value}`")

                    # Confidence note
                    if f.confidence_note:
                        st.caption(f"Note: {f.confidence_note}")

                    # Field Action Buttons
                    col_act1, col_act2, col_act3 = st.columns([1.6, 1.4, 0.6])
                    with col_act1:
                        if st.button("Save & Validate", key=f"btn_save_{f.id}", use_container_width=True):
                            val_res = FieldValidator.validate_field(
                                field_name=f.field_name,
                                value=edited_val,
                                data_type=f.data_type,
                                is_user_corrected=True,
                            )
                            field_repo.update_field(
                                field_id=f.id,
                                value=edited_val,
                                normalized_value=val_res.normalized_value,
                                validation_status=val_res.status,
                                review_status="verified" if val_res.is_valid else "flagged",
                                is_user_corrected=True,
                            )
                            audit_repo.log(
                                document_id=active_doc.id,
                                field_id=f.id,
                                field_name=f.field_name,
                                action="corrected",
                                old_value=f.extracted_value,
                                new_value=edited_val,
                                note="User edited value and triggered validation.",
                            )
                            st.success(f"Updated '{f.field_name}'!")
                            st.rerun()

                    with col_act2:
                        is_already_verified = f.review_status == "verified"
                        if st.button("Verify Field", key=f"btn_ver_{f.id}", disabled=is_already_verified, use_container_width=True):
                            field_repo.update_field(
                                field_id=f.id,
                                value=f.extracted_value,
                                normalized_value=f.normalized_value,
                                validation_status=f.validation_status,
                                review_status="verified",
                                is_user_corrected=bool(f.is_user_corrected),
                            )
                            audit_repo.log(
                                document_id=active_doc.id,
                                field_id=f.id,
                                field_name=f.field_name,
                                action="verified",
                                old_value=f.extracted_value,
                                new_value=f.extracted_value,
                                note="User explicitly approved field as verified.",
                            )
                            st.rerun()

                    with col_act3:
                        if st.button("Delete", key=f"btn_del_{f.id}", help="Delete field"):
                            field_repo.delete(f.id)
                            audit_repo.log(
                                document_id=active_doc.id,
                                field_id=f.id,
                                field_name=f.field_name,
                                action="deleted",
                                note="User deleted field.",
                            )
                            st.rerun()

                    st.divider()

        # Add Custom Field Section
        with st.expander("Add Custom Field to Document"):
            cf_col1, cf_col2 = st.columns(2)
            with cf_col1:
                cf_name = st.text_input("Field Name", key="cf_name_inp", placeholder="e.g. tax_id")
            with cf_col2:
                cf_type = st.selectbox("Data Type", ["string", "date", "monetary", "email", "phone", "number"], key="cf_type_sel")
            cf_val = st.text_input("Initial Value", key="cf_val_inp", placeholder="e.g. 12-3456789")

            if st.button("Add & Validate Field", key="btn_add_cf", use_container_width=True):
                if cf_name.strip():
                    val_res = FieldValidator.validate_field(
                        field_name=cf_name.strip(),
                        value=cf_val.strip(),
                        data_type=cf_type,
                        is_user_corrected=True,
                    )
                    import uuid
                    new_f = ExtractedFieldRecord(
                        id=str(uuid.uuid4()),
                        document_id=active_doc.id,
                        field_name=cf_name.strip(),
                        extracted_value=cf_val.strip(),
                        normalized_value=val_res.normalized_value,
                        data_type=cf_type,
                        source_page=current_page,
                        evidence_excerpt="User manually defined field",
                        bounding_box=None,
                        extraction_method="user_manual",
                        validation_status=val_res.status,
                        review_status="verified",
                        is_user_corrected=1,
                        confidence_note="Created manually by user",
                        created_at=now_utc_iso(),
                        updated_at=now_utc_iso(),
                    )
                    field_repo.insert_batch([new_f])
                    audit_repo.log(
                        document_id=active_doc.id,
                        field_id=new_f.id,
                        field_name=new_f.field_name,
                        action="custom_field_added",
                        new_value=cf_val.strip(),
                        note="Manually created by user.",
                    )
                    st.success(f"Added custom field '{cf_name}'!")
                    st.rerun()

        # Reprocess Options
        with st.expander("Reprocess Document"):
            t_names = [t["name"] for t in pipeline.template_mgr.list_templates()]
            cur_idx = t_names.index(active_doc.selected_template) if active_doc.selected_template in t_names else 0
            new_template = st.selectbox("Change Template", t_names, index=cur_idx, key="rp_template_sel")
            rp_force_ocr = st.checkbox("Force OCR during reprocess", value=False, key="rp_ocr_chk")

            if st.button("Reprocess Now", key="btn_rp_exec", use_container_width=True):
                with st.spinner("Reprocessing document..."):
                    try:
                        pipeline.reprocess_document(
                            document_id=active_doc.id,
                            template_name=new_template,
                            force_ocr=rp_force_ocr,
                        )
                        st.success("Reprocessing complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Reprocess error: {e}")

        # Quick Export Link
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("Export Extracted Data", type="primary", use_container_width=True):
            st.session_state["export_selected_doc_id"] = active_doc.id
            st.session_state["current_page"] = "Export Center"
            st.rerun()
