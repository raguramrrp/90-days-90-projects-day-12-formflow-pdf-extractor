"""Templates & Rules View for FormFlow matching the design system."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from src.templates.manager import TemplateManager
from src.ui.components import get_icon_svg, render_top_navigation, safe_html


def render_templates_view(template_mgr: TemplateManager) -> None:
    """Render the extraction template manager and regex rule playground."""
    render_top_navigation()

    tpl_icon = get_icon_svg("templates", color="#2563EB", size=24)
    header_html = f"""
    <div class="ff-hero-container" style="padding: 16px 22px; margin-bottom: 16px;">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box" style="width: 44px; height: 44px;">
                {tpl_icon}
            </div>
            <div>
                <span class="ff-hero-pill">Schema & Extraction Rules</span>
                <h2 class="ff-hero-title" style="font-size: 1.35rem; margin: 0 0 2px 0;">Templates & Extraction Rules</h2>
                <p class="ff-hero-subtitle" style="font-size: 0.82rem;">
                    Define reusable schemas, context label aliases, and deterministic regex patterns for recurring document types.
                </p>
            </div>
        </div>
    </div>
    """
    safe_html(header_html)

    templates = template_mgr.list_templates()
    template_names = [t["name"] for t in templates]

    tab_inspect, tab_create, tab_tester = st.tabs(["Inspect Templates", "Create New Template", "Regex & Rule Tester"])

    # =========================================================================
    # TAB 1: INSPECT TEMPLATES
    # =========================================================================
    with tab_inspect:
        col_sel, col_del = st.columns([3, 1])
        with col_sel:
            selected_name = st.selectbox("Select Template to Inspect", template_names, key="tpl_inspect_sel")

        tpl = template_mgr.get_template(selected_name)
        if tpl:
            with col_del:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if not tpl.get("is_builtin"):
                    if st.button("Delete Template", key=f"del_tpl_{tpl['id']}", use_container_width=True):
                        template_mgr.delete_template(tpl["id"])
                        st.success(f"Deleted custom template '{tpl['name']}'")
                        st.rerun()
                else:
                    st.caption("Built-in template (Protected)")

            tpl_title_html = f"""
            <div style="margin: 8px 0 12px 0;">
                <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--ff-text-primary); margin: 0 0 4px 0;">
                    {tpl['name']} <span style="font-size: 0.80rem; font-weight: normal; color: var(--ff-accent); background: var(--ff-accent-light); padding: 2px 8px; border-radius: 6px;">{tpl['category']}</span>
                </h3>
                <p style="color: var(--ff-text-secondary); font-size: 0.85rem; margin: 0;">{tpl['description']}</p>
            </div>
            """
            safe_html(tpl_title_html)

            fields_dict = tpl.get("rules", {}).get("fields", {})
            st.markdown(f"**Configured Extraction Fields ({len(fields_dict)}):**")

            field_rows = []
            for f_name, f_spec in fields_dict.items():
                field_rows.append(
                    {
                        "Field Key": f_name,
                        "Data Type": f_spec.get("data_type", "string"),
                        "Required": "Yes" if f_spec.get("required") else "No",
                        "Label Aliases": ", ".join(f_spec.get("aliases", [])),
                        "Regex Pattern": f_spec.get("pattern", "—"),
                    }
                )

            st.dataframe(pd.DataFrame(field_rows), use_container_width=True, hide_index=True)

            with st.expander("View Raw JSON Specification"):
                st.json(tpl["rules"])

    # =========================================================================
    # TAB 2: CREATE NEW TEMPLATE
    # =========================================================================
    with tab_create:
        st.markdown("#### Define New Document Template")
        c_name, c_cat = st.columns([2, 1])
        with c_name:
            new_name = st.text_input("Template Name", placeholder="e.g. Purchase Order, Travel Claim", key="new_tpl_name")
        with c_cat:
            new_cat = st.selectbox("Category", ["Invoices & Finance", "HR & Registration", "Legal & Contracts", "Custom"], key="new_tpl_cat")

        new_desc = st.text_area("Description", placeholder="Describe document purpose and expected format", key="new_tpl_desc", height=80)

        st.markdown("**Add Field Extraction Specifications**")
        if "custom_fields_builder" not in st.session_state:
            st.session_state["custom_fields_builder"] = [
                {"name": "order_id", "type": "string", "required": True, "aliases": "Order ID, PO #, PO Number", "pattern": r"PO-[0-9]{4,8}"}
            ]

        for idx, item in enumerate(st.session_state["custom_fields_builder"]):
            c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.5, 1.2, 0.8, 2, 0.5])
            with c_f1:
                item["name"] = st.text_input("Field Key", value=item["name"], key=f"f_name_{idx}")
            with c_f2:
                item["type"] = st.selectbox("Data Type", ["string", "date", "monetary", "email", "phone", "number"], index=["string", "date", "monetary", "email", "phone", "number"].index(item["type"]), key=f"f_type_{idx}")
            with c_f3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                item["required"] = st.checkbox("Req.", value=item["required"], key=f"f_req_{idx}")
            with c_f4:
                item["aliases"] = st.text_input("Context Aliases (comma-separated)", value=item["aliases"], key=f"f_alias_{idx}")
            with c_f5:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("✕", key=f"f_del_{idx}"):
                    st.session_state["custom_fields_builder"].pop(idx)
                    st.rerun()

        if st.button("Add Another Field to Schema", key="btn_add_schema_f"):
            st.session_state["custom_fields_builder"].append({"name": "", "type": "string", "required": False, "aliases": "", "pattern": ""})
            st.rerun()

        st.divider()
        if st.button("Save New Template", type="primary", use_container_width=True):
            if not new_name.strip():
                st.error("Template name cannot be empty.")
            else:
                fields_spec = {}
                for itm in st.session_state["custom_fields_builder"]:
                    if itm["name"].strip():
                        aliases_list = [a.strip() for a in itm["aliases"].split(",") if a.strip()]
                        fields_spec[itm["name"].strip()] = {
                            "data_type": itm["type"],
                            "required": itm["required"],
                            "aliases": aliases_list,
                            "pattern": itm.get("pattern") or None,
                        }
                res = template_mgr.create_template(
                    name=new_name.strip(),
                    category=new_cat,
                    description=new_desc.strip(),
                    rules={"fields": fields_spec},
                )
                st.success(f"Created template '{res['name']}' successfully!")
                st.session_state["custom_fields_builder"] = [
                    {"name": "order_id", "type": "string", "required": True, "aliases": "Order ID, PO #, PO Number", "pattern": r"PO-[0-9]{4,8}"}
                ]
                st.rerun()

    # =========================================================================
    # TAB 3: REGEX & RULE TESTER PLAYGROUND
    # =========================================================================
    with tab_tester:
        st.markdown("#### Test Regular Expressions on Document Excerpts")
        regex_input = st.text_input("Regex Pattern", value=r"(?i)(?:invoice|inv)[\s#:]*([A-Z0-9-]{4,15})", key="rgx_test_inp")
        test_corpus = st.text_area(
            "Document Text Sample",
            value="Apex Cloud Solutions Inc.\nInvoice Number: INV-2026-8891\nDate: 2026-10-15\nTotal Due: $1,569.63",
            height=120,
            key="rgx_corpus_inp",
        )

        if st.button("Execute Regex Scan", key="btn_exec_rgx", type="secondary"):
            if regex_input.strip() and test_corpus.strip():
                try:
                    matches = list(re.finditer(regex_input, test_corpus))
                    if matches:
                        st.success(f"Found {len(matches)} match(es)!")
                        m_rows = []
                        for idx, m in enumerate(matches, 1):
                            m_rows.append(
                                {
                                    "Match #": idx,
                                    "Full Span": f"{m.start()}–{m.end()}",
                                    "Full Match": m.group(0),
                                    "Capture Group 1": m.group(1) if m.groups() else "—",
                                }
                            )
                        st.dataframe(pd.DataFrame(m_rows), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No matches found in the provided text.")
                except Exception as e:
                    st.error(f"Invalid Regex Pattern: {e}")
