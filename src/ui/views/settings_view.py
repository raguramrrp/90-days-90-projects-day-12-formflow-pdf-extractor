"""Settings and Storage Management View for FormFlow matching the design system."""

from __future__ import annotations

import os
from pathlib import Path
import streamlit as st

from config import DATA_STORAGE_DIR, DATABASE_PATH
from src.core.ocr_engine import OCREngine
from src.ui.components import get_icon_svg, render_top_navigation, safe_html


def render_settings_view() -> None:
    """Render the configuration and storage center."""
    render_top_navigation()

    settings_icon = get_icon_svg("settings", color="#2563EB", size=24)
    header_html = f"""
    <div class="ff-hero-container" style="padding: 16px 22px; margin-bottom: 16px;">
        <div class="ff-hero-left">
            <div class="ff-hero-icon-box" style="width: 44px; height: 44px;">
                {settings_icon}
            </div>
            <div>
                <span class="ff-hero-pill">System Administration</span>
                <h2 class="ff-hero-title" style="font-size: 1.35rem; margin: 0 0 2px 0;">Settings & Preferences</h2>
                <p class="ff-hero-subtitle" style="font-size: 0.82rem;">
                    Manage interface appearance and inspect local storage footprint.
                </p>
            </div>
        </div>
    </div>
    """
    safe_html(header_html)

    tab_theme, tab_storage = st.tabs(["Theme & Appearance", "Storage Management"])

    # =========================================================================
    # TAB 1: THEME & APPEARANCE
    # =========================================================================
    with tab_theme:
        st.markdown("#### Interface Theme Preferences")
        st.caption("FormFlow uses a calibrated enterprise palette with accessible contrast ratios, neutral grays, and muted blue accents.")

        cur_dark = st.session_state.get("dark_mode", False)
        dark_toggle = st.toggle("Enable Dark Theme", value=cur_dark, help="Switches between Clean Light and Deep Navy Dark themes.")

        if dark_toggle != cur_dark:
            st.session_state["dark_mode"] = dark_toggle
            st.rerun()

        theme_mode_desc = "**Dark Mode Active** — Optimized for low-light environments." if cur_dark else "**Light Mode Active** — Enterprise SaaS document workspace styling."
        st.markdown(theme_mode_desc)

    # =========================================================================
    # TAB 2: STORAGE MANAGEMENT
    # =========================================================================
    with tab_storage:
        st.markdown("#### Local Storage & Database Footprint")
        storage_files = list(DATA_STORAGE_DIR.glob("*"))
        storage_size_bytes = sum(f.stat().st_size for f in storage_files if f.is_file())
        db_size_bytes = DATABASE_PATH.stat().st_size if DATABASE_PATH.exists() else 0

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Stored PDF Files", len(storage_files))
        with col_s2:
            st.metric("Storage Folder Size", f"{storage_size_bytes / (1024 * 1024):.2f} MB")
        with col_s3:
            st.metric("SQLite DB Size", f"{db_size_bytes / 1024:.1f} KB")

        st.divider()
        st.markdown("#### Storage Maintenance Operations")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if st.button("Clear OCR In-Memory Cache", use_container_width=True):
                OCREngine._cache.clear()
                st.toast("OCR cache cleared.")
        with col_m2:
            if st.button("Vacuum SQLite Database", use_container_width=True):
                from src.database.db import get_db_connection
                with get_db_connection() as conn:
                    conn.execute("VACUUM;")
                st.toast("SQLite database vacuumed successfully.")
