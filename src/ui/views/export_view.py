"""Export Center View for FormFlow matching the design system."""

from __future__ import annotations

import io
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st

from src.database.models import DocumentRecord, DocumentRepository, ExtractedFieldRecord, FieldRepository
from src.exporters.csv_exporter import CSVExporter
from src.exporters.json_exporter import JSONExporter
from src.ui.components import get_icon_svg, render_status_badge, render_top_navigation, safe_html


def render_export_view(doc_repo: DocumentRepository, field_repo: FieldRepository) -> None:
    """Render the structured export center with JSON and CSV options and formula protection."""
    render_top_navigation()

    export_icon = get_icon_svg("export", color="#2563EB", size=24)
    header_html = f"""
    <div class="ff-hero-container" style="padding: 16px 22px; margin-bottom: 20px;">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box" style="width: 44px; height: 44px;">
                {export_icon}
            </div>
            <div>
                <span class="ff-hero-pill">Dataset Exporter</span>
                <h2 class="ff-hero-title" style="font-size: 1.35rem; margin: 0 0 2px 0;">Export Center</h2>
                <p class="ff-hero-subtitle" style="font-size: 0.82rem;">
                    Export validated and reviewed structured data to documented JSON schemas and formula-sanitized CSV files.
                </p>
            </div>
        </div>
    </div>
    """
    safe_html(header_html)

    all_docs = doc_repo.list_all(limit=500)
    if not all_docs:
        st.info("No documents found in the database. Please process a document first.")
        return

    st.markdown("### Export Configuration")

    # =========================================================================
    # ROW 1: SOURCE SCOPE & DOCUMENT SELECTION
    # =========================================================================
    col_scope, col_doc_sel = st.columns([1.1, 1.9], gap="large")

    with col_scope:
        scope = st.radio(
            "Export Target Scope",
            ["Selected Document", "Batch (All Documents)"],
            horizontal=False,
            help="Export a single focused document or aggregate all documents across your entire local repository.",
        )

    selected_doc: Optional[DocumentRecord] = None
    with col_doc_sel:
        if scope == "Selected Document":
            preselect_id = st.session_state.get("export_selected_doc_id") or st.session_state.get("active_doc_id")
            doc_options = {f"{d.filename} ({d.id[:8]})": d for d in all_docs}
            default_idx = 0
            if preselect_id:
                for idx, d in enumerate(all_docs):
                    if d.id == preselect_id:
                        default_idx = idx
                        break

            selected_label = st.selectbox("Choose Document to Export", list(doc_options.keys()), index=default_idx)
            selected_doc = doc_options[selected_label]
            doc_fields = field_repo.get_by_document(selected_doc.id)
            verified_count = sum(1 for f in doc_fields if f.review_status == "verified")
            status_clean = (selected_doc.processing_status or "completed").replace("_", " ").title()

            st.caption(
                f"Selected: **{selected_doc.filename}** • {selected_doc.page_count} page(s) • "
                f"{len(doc_fields)} fields ({verified_count} verified) • Status: {status_clean}"
            )
        else:
            st.markdown("<label style='font-size:0.88rem; font-weight:600;'>Batch Summary</label>", unsafe_allow_html=True)
            st.info(f"All **{len(all_docs)}** document(s) in repository will be aggregated into the export package.")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # ROW 2: FORMAT SELECTION & DATA CLEANING FILTERS
    # =========================================================================
    col_fmt, col_filters = st.columns([1.1, 1.9], gap="large")

    with col_fmt:
        export_format = st.selectbox(
            "File Format",
            ["JSON", "CSV"],
            help="JSON preserves nested metadata; CSV generates spreadsheet-compatible tables for Excel and Pandas.",
        )

        csv_layout = "Long (One row per field)"
        if export_format == "CSV":
            csv_layout = st.radio(
                "CSV Table Structure",
                ["Wide (One row per document)", "Long (One row per field)"],
                horizontal=False,
                help="Wide format creates a spreadsheet with one column per field (ideal for Excel). Long format lists one row per extracted field.",
            )

    with col_filters:
        st.markdown("<label style='font-size:0.88rem; font-weight:600;'>Data Quality & Inclusion Filters</label>", unsafe_allow_html=True)
        only_verified = st.checkbox(
            "Only include Verified fields",
            value=False,
            help="Excludes unverified, unreviewed, or pending fields from the exported dataset.",
        )
        exclude_invalid = st.checkbox(
            "Exclude Invalid / Missing fields",
            value=True,
            help="Removes fields that failed validation rules or have no extracted content.",
        )
        st.caption("Filters apply deterministically to both live preview and generated files.")

    # Gather data items: List[Tuple[DocumentRecord, List[ExtractedFieldRecord]]]
    items: List[Tuple[DocumentRecord, List[ExtractedFieldRecord]]] = []
    if scope == "Selected Document" and selected_doc:
        fields = field_repo.get_by_document(selected_doc.id)
        items.append((selected_doc, fields))
    else:
        for d in all_docs:
            f_list = field_repo.get_by_document(d.id)
            items.append((d, f_list))

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Security Alert Card: Formula Injection Protection
    st.info(
        "Formula Injection Protection Active: Values starting with =, +, -, @ "
        "are sanitized with a leading quote to prevent spreadsheet macro execution in Microsoft Excel and Google Sheets."
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # SECTION 3: LIVE EXPORT PREVIEW & DOWNLOAD
    # =========================================================================
    st.markdown("### Live Export Preview")

    if export_format == "JSON":
        if scope == "Selected Document" and selected_doc:
            doc_item, f_item = items[0]
            json_str = JSONExporter.export_document(doc_item, f_item, only_verified=only_verified, exclude_invalid=exclude_invalid)
            file_name = f"{selected_doc.filename.rsplit('.', 1)[0]}_extracted.json"
        else:
            json_str = JSONExporter.export_batch(items, only_verified=only_verified, exclude_invalid=exclude_invalid)
            file_name = "formflow_batch_export.json"

        st.download_button(
            label=f"Download JSON ({len(json_str)} bytes)",
            data=json_str,
            file_name=file_name,
            mime="application/json",
            type="primary",
            use_container_width=True,
        )

        st.json(json_str)

    elif export_format == "CSV":
        is_wide = "Wide" in csv_layout
        csv_str = CSVExporter.export(
            items,
            wide_format=is_wide,
            only_verified=only_verified,
            exclude_invalid=exclude_invalid,
        )

        if scope == "Selected Document" and selected_doc:
            file_name = f"{selected_doc.filename.rsplit('.', 1)[0]}_{'wide' if is_wide else 'long'}.csv"
        else:
            file_name = f"formflow_batch_{'wide' if is_wide else 'long'}.csv"

        st.download_button(
            label=f"Download Sanitized CSV ({len(csv_str)} bytes)",
            data=csv_str.encode("utf-8-sig"),
            file_name=file_name,
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )

        try:
            df_preview = pd.read_csv(io.StringIO(csv_str))
            st.dataframe(df_preview, use_container_width=True)
        except Exception:
            st.text_area("CSV Raw Output", csv_str, height=220)
