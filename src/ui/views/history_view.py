"""Documents & History View for FormFlow matching the design system."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from src.core.pipeline import ExtractionPipeline
from src.database.models import AuditLogRepository, DocumentRepository, FieldRepository
from src.ui.components import get_icon_svg, render_status_badge, render_top_navigation, safe_html


def render_history_view(
    pipeline: ExtractionPipeline,
    doc_repo: DocumentRepository,
    field_repo: FieldRepository,
    audit_repo: AuditLogRepository,
) -> None:
    """Render the searchable and filterable document history interface."""
    render_top_navigation()

    history_icon = get_icon_svg("history", color="#2563EB", size=24)
    header_html = f"""
    <div class="ff-hero-container" style="padding: 16px 22px; margin-bottom: 16px;">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box" style="width: 44px; height: 44px;">
                {history_icon}
            </div>
            <div>
                <span class="ff-hero-pill">Audit & Document Archive</span>
                <h2 class="ff-hero-title" style="font-size: 1.35rem; margin: 0 0 2px 0;">Documents & Extraction History</h2>
                <p class="ff-hero-subtitle" style="font-size: 0.82rem;">
                    Search, filter, and inspect past document extraction runs, validation states, and full audit trails across all sessions.
                </p>
            </div>
        </div>
    </div>
    """
    safe_html(header_html)

    # Filter Section
    st.markdown("#### Filter Archive")
    col_search, col_status, col_template = st.columns([2, 1, 1])
    with col_search:
        search_query = st.text_input(
            "Search Archive",
            placeholder="Search Filename or Document ID (e.g. invoice, APP-9021)",
            key="hist_search",
            label_visibility="collapsed",
        )
    with col_status:
        status_filter = st.selectbox(
            "Status",
            ["All", "completed", "completed_with_warnings", "review_required", "failed", "processing"],
            key="hist_status",
            label_visibility="collapsed",
        )
    with col_template:
        all_templates = ["All"] + [t["name"] for t in pipeline.template_mgr.list_templates()]
        template_filter = st.selectbox("Template", all_templates, key="hist_template", label_visibility="collapsed")

    # Fetch matching records
    documents = doc_repo.list_all(
        search_query=search_query if search_query.strip() else None,
        status_filter=status_filter,
        template_filter=template_filter,
        limit=200,
    )

    if not documents:
        st.info("No matching documents found in SQLite database.")
        return

    st.caption(f"Showing **{len(documents)}** document(s) in repository.")
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Tabular presentation
    for doc in documents:
        fields = field_repo.get_by_document(doc.id)
        verified_count = sum(1 for f in fields if f.review_status == "verified")
        warnings_count = sum(1 for f in fields if f.validation_status in ("warning", "invalid", "missing"))
        file_exists = Path(doc.file_path).exists()

        col_info, col_status_badge, col_actions = st.columns([4.2, 1.8, 2.5])

        with col_info:
            doc_title_html = f"<div style='font-size: 0.98rem; font-weight: 700; color: var(--ff-text-primary);'>{doc.filename}</div>"
            safe_html(doc_title_html)
            upload_str = (doc.upload_time or "")[:19].replace("T", " ")
            st.caption(
                f"ID: `{doc.id[:8]}` • Size: {doc.file_size / 1024:.1f} KB • Pages: {doc.page_count} • "
                f"Uploaded: {upload_str} • Template: **{doc.selected_template or 'None'}**"
            )
            if not file_exists:
                st.caption("*Original PDF removed from storage; metadata and extracted fields remain in SQLite.*")

        with col_status_badge:
            safe_html(render_status_badge(doc.processing_status))
            st.caption(f"{verified_count}/{len(fields)} fields verified")
            if warnings_count:
                warn_html = f"<div style='color: #DC2626; font-size: 0.75rem; font-weight:600;'>{warnings_count} warnings</div>"
                safe_html(warn_html)

        with col_actions:
            col_a1, col_a2, col_a3 = st.columns([1.2, 1.2, 0.8])
            with col_a1:
                if st.button("Review", key=f"hist_rev_{doc.id}", use_container_width=True):
                    st.session_state["active_doc_id"] = doc.id
                    st.session_state[f"page_num_{doc.id}"] = 1
                    st.session_state["current_page"] = "Extract & Review"
                    st.rerun()
            with col_a2:
                if st.button("Export", key=f"hist_exp_{doc.id}", use_container_width=True):
                    st.session_state["export_selected_doc_id"] = doc.id
                    st.session_state["current_page"] = "Export Center"
                    st.rerun()
            with col_a3:
                if st.button("Delete", key=f"hist_del_{doc.id}", help="Delete document and audit log from SQLite"):
                    doc_repo.delete(doc.id)
                    st.toast(f"Deleted {doc.filename}")
                    st.rerun()

        # Audit Trail Drawer per document
        with st.expander(f"Audit Trail ({doc.filename})"):
            audits = audit_repo.get_by_document(doc.id)
            if not audits:
                st.caption("No audit entries recorded for this document yet.")
            else:
                audit_rows = []
                for a in audits:
                    ts = a.get("timestamp", a.get("created_at", ""))
                    ts_clean = ts[:19].replace("T", " ") if ts else "—"
                    audit_rows.append(
                        {
                            "Timestamp": ts_clean,
                            "Field": a.get("field_name") or "—",
                            "Action": a.get("action", "—"),
                            "Old Value": a.get("old_value") or "—",
                            "New Value": a.get("new_value") or "—",
                            "Note": a.get("note") or "—",
                        }
                    )
                st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

        st.divider()
