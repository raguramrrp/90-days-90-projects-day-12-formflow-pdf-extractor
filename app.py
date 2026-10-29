"""FormFlow: Intelligent PDF Form Field Extraction Pipeline.

Main Streamlit Application Entrypoint matching the AI reference design.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from config import APP_NAME, APP_TITLE, APP_VERSION
from src.core.pipeline import ExtractionPipeline
from src.database.db import init_db
from src.database.models import AuditLogRepository, DocumentRepository, FieldRepository
from src.templates.manager import TemplateManager
from src.ui.components import get_icon_svg, safe_html
from src.ui.theme import inject_theme
from src.ui.views.export_view import render_export_view
from src.ui.views.extract_review_view import render_extract_review_view
from src.ui.views.history_view import render_history_view
from src.ui.views.settings_view import render_settings_view
from src.ui.views.templates_view import render_templates_view
from src.ui.views.workspace_view import render_workspace_view

# Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} — PDF Extraction Pipeline",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_app_services():
    """Initialize database and repositories in session state."""
    init_db()
    if "pipeline" not in st.session_state:
        doc_repo = DocumentRepository()
        field_repo = FieldRepository()
        template_mgr = TemplateManager()
        audit_repo = AuditLogRepository()
        pipeline = ExtractionPipeline(
            doc_repo=doc_repo,
            field_repo=field_repo,
            template_mgr=template_mgr,
            audit_repo=audit_repo,
        )
        st.session_state["doc_repo"] = doc_repo
        st.session_state["field_repo"] = field_repo
        st.session_state["template_mgr"] = template_mgr
        st.session_state["audit_repo"] = audit_repo
        st.session_state["pipeline"] = pipeline


def main():
    initialize_app_services()
    inject_theme()

    doc_repo: DocumentRepository = st.session_state["doc_repo"]
    field_repo: FieldRepository = st.session_state["field_repo"]
    template_mgr: TemplateManager = st.session_state["template_mgr"]
    audit_repo: AuditLogRepository = st.session_state["audit_repo"]
    pipeline: ExtractionPipeline = st.session_state["pipeline"]

    # Session State defaults
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Workspace"
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False

    # =========================================================================
    # SIDEBAR: CLEAN ENTERPRISE NAVIGATION
    # =========================================================================
    with st.sidebar:
        # Brand Header (Subtext & Meta removed as requested)
        logo_svg = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#2563EB"/><path d="M2 17L12 22L22 17" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

        brand_html = f"""
        <div style="padding: 2px 0 12px 0; border-bottom: 1px solid var(--ff-border); margin-bottom: 16px;">
            <div class="ff-sidebar-header">
                <div class="ff-sidebar-brand">
                    <div class="ff-sidebar-logo" style="background: transparent;">
                        {logo_svg}
                    </div>
                    <div class="ff-sidebar-title">{APP_NAME}</div>
                </div>
            </div>
            <div class="ff-sidebar-subtitle">PDF Form Field Extraction Pipeline</div>
        </div>
        """
        safe_html(brand_html)

        # Clean Sidebar Navigation Buttons matching reference design
        nav_items = [
            ("Workspace", "Workspace"),
            ("Extract & Review", "Extract & Review"),
            ("Documents & History", "Documents & History"),
            ("Templates & Rules", "Templates & Rules"),
            ("Export Center", "Export Center"),
            ("Settings & Privacy", "Settings & Privacy"),
        ]

        for route_key, display_label in nav_items:
            is_active = (st.session_state["current_page"] == route_key)
            btn_type = "primary" if is_active else "secondary"
            if st.button(display_label, key=f"nav_btn_{route_key}", use_container_width=True, type=btn_type):
                if st.session_state["current_page"] != route_key:
                    st.session_state["current_page"] = route_key
                    st.rerun()

        # Active Document card in sidebar
        active_id = st.session_state.get("active_doc_id")
        active_doc = doc_repo.get_by_id(active_id) if active_id else None
        if not active_doc:
            recent = doc_repo.list_all(limit=1)
            if recent:
                active_doc = recent[0]
                st.session_state["active_doc_id"] = active_doc.id

        doc_icon_svg = get_icon_svg("document", color="#2563EB", size=18)
        chevron_svg = get_icon_svg("chevron_right", color="#94A3B8", size=14)

        if active_doc:
            status_clean = (active_doc.processing_status or "completed").replace("_", " ").title()
            dot_color = "#059669" if "completed" in active_doc.processing_status.lower() and "warning" not in active_doc.processing_status.lower() else "#D97706"
            if "failed" in active_doc.processing_status.lower() or "review" in active_doc.processing_status.lower():
                dot_color = "#DC2626"

            active_doc_html = f"""
            <div style="height: 14px;"></div>
            <div class="ff-sidebar-card">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 28px; height: 28px; background: var(--ff-accent-light); border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                            {doc_icon_svg}
                        </div>
                        <div>
                            <div class="ff-sidebar-card-label">Active Document</div>
                            <div class="ff-sidebar-card-title" title="{active_doc.filename}">{active_doc.filename}</div>
                        </div>
                    </div>
                    <div>{chevron_svg}</div>
                </div>
                <div style="font-size: 0.72rem; color: var(--ff-text-secondary); margin-top: 6px; display: flex; align-items: center; gap: 5px;">
                    <span style="color: {dot_color}; font-size: 0.75rem;">●</span> {status_clean}
                </div>
            </div>
            """
            safe_html(active_doc_html)

        # Bottom Promo / Insight Card
        promo_html = """
        <div class="ff-sidebar-promo">
            <h4 class="ff-sidebar-promo-title">Smarter Documents, Better Insights</h4>
            <p class="ff-sidebar-promo-sub">Extract. Validate. Organize.</p>
        </div>
        """
        safe_html(promo_html)

    # =========================================================================
    # ROUTE TO CURRENT VIEW
    # =========================================================================
    page = st.session_state["current_page"]
    if page == "Workspace":
        render_workspace_view(pipeline, doc_repo)
    elif page == "Extract & Review":
        render_extract_review_view(pipeline, doc_repo, field_repo, audit_repo)
    elif page == "Documents & History":
        render_history_view(pipeline, doc_repo, field_repo, audit_repo)
    elif page == "Templates & Rules":
        render_templates_view(template_mgr)
    elif page == "Export Center":
        render_export_view(doc_repo, field_repo)
    elif page == "Settings & Privacy":
        render_settings_view()


if __name__ == "__main__":
    main()
