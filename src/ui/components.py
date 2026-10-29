"""Reusable UI components, SVG icons, and interactive topbar for FormFlow."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional
import streamlit as st


def clean_html(raw_html: str) -> str:
    """Strip leading/trailing whitespace and remove empty lines to prevent Streamlit Markdown leaks."""
    lines = [line.strip() for line in raw_html.strip().splitlines() if line.strip()]
    return "".join(lines)


def safe_html(raw_html: str) -> None:
    """Safely render HTML in Streamlit without code block splitting or tag leaks."""
    st.markdown(clean_html(raw_html), unsafe_allow_html=True)


def get_icon_svg(name: str, color: str = "#2563EB", size: int = 18) -> str:
    """Return inline SVG string for professional line icons without relying on emojis."""
    icons: Dict[str, str] = {
        "workspace": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        "extract": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="11" cy="14" r="3"/><line x1="13.5" y1="16.5" x2="17" y2="20"/></svg>',
        "history": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        "templates": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>',
        "export": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
        "settings": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        "document": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>',
        "check_shield": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
        "check_circle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        "alert_triangle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        "alert_circle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        "lightning": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        "user": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        "calendar": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
        "building": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><line x1="9" y1="22" x2="9" y2="22.01"/><line x1="15" y1="22" x2="15" y2="22.01"/><line x1="9" y1="16" x2="9" y2="16.01"/><line x1="15" y1="16" x2="15" y2="16.01"/><line x1="9" y1="10" x2="9" y2="10.01"/><line x1="15" y1="10" x2="15" y2="10.01"/><line x1="9" y1="4" x2="9" y2="4.01"/><line x1="15" y1="4" x2="15" y2="4.01"/></svg>',
        "image": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
        "chevron_right": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
        "cloud_upload": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 16l-4-4-4 4"/><path d="M12 12v9"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/><polyline points="16 16 12 12 8 16"/></svg>',
        "search": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    }
    return icons.get(name, icons["document"])


def render_status_badge(status: str) -> str:
    """Return HTML markup for standard validation or processing status badges."""
    clean_status = (status or "unverified").lower().replace(" ", "_")
    mapping = {
        "valid": ("ff-status-valid", "Valid"),
        "warning": ("ff-status-warning", "Warning"),
        "invalid": ("ff-status-invalid", "Invalid"),
        "missing": ("ff-status-missing", "Missing"),
        "unverified": ("ff-status-unverified", "Unverified"),
        "corrected": ("ff-status-corrected", "Corrected"),
        "completed": ("ff-status-completed", "Completed"),
        "completed_with_warnings": ("ff-status-completed-warnings", "Warnings"),
        "review_required": ("ff-status-review", "Review Req."),
        "processing": ("ff-status-processing", "Processing"),
        "uploaded": ("ff-status-unverified", "Uploaded"),
        "failed": ("ff-status-failed", "Failed"),
        "verified": ("ff-status-valid", "Verified"),
        "pending": ("ff-status-unverified", "Pending"),
        "flagged": ("ff-status-warning", "Flagged"),
    }

    css_class, display_text = mapping.get(clean_status, ("ff-status-unverified", status.title()))
    return f'<span class="ff-status-pill {css_class}">{display_text}</span>'


def render_metric_card(
    label: str,
    value: Any,
    subtext: Optional[str] = None,
    icon_type: str = "document",
    icon_color: str = "#2563EB",
    icon_bg: str = "#EFF6FF",
) -> None:
    """Render a premium metric KPI card matching the reference design."""
    is_dark = st.session_state.get("dark_mode", False)
    if is_dark:
        if icon_color == "#2563EB":
            icon_color = "#93C5FD"
            icon_bg = "#1E3A8A"
        elif icon_color == "#059669":
            icon_color = "#6EE7B7"
            icon_bg = "#064E3B"
        elif icon_color == "#D97706":
            icon_color = "#FCD34D"
            icon_bg = "#78350F"
        elif icon_color == "#DC2626":
            icon_color = "#FCA5A5"
            icon_bg = "#7F1D1D"

    subtext_html = f'<div class="ff-metric-subtext">{subtext}</div>' if subtext else ""
    icon_svg = get_icon_svg(icon_type, color=icon_color, size=20)
    chevron_svg = get_icon_svg("chevron_right", color="#64748B" if is_dark else "#94A3B8", size=16)

    html = f"""
    <div class="ff-metric-card">
        <div class="ff-metric-top">
            <div class="ff-metric-icon" style="background-color: {icon_bg};">
                {icon_svg}
            </div>
            <div class="ff-metric-label-group">
                <span class="ff-metric-label">{label}</span>
            </div>
            <div class="ff-metric-chevron">
                {chevron_svg}
            </div>
        </div>
        <div class="ff-metric-value">{value}</div>
        {subtext_html}
    </div>
    """
    safe_html(html)


def render_top_navigation():
    """Render the interactive top search, clean theme icon toggle, notifications, and profile."""
    is_dark = st.session_state.get("dark_mode", False)

    col_search, col_theme, col_notify, col_user = st.columns([6.4, 0.7, 0.7, 2.2], gap="small")

    with col_search:
        search_query = st.text_input(
            "Global Search",
            key="global_search_input",
            placeholder="Search documents, templates, fields... (Press Enter)",
            label_visibility="collapsed",
        )
        if search_query and search_query.strip():
            st.session_state["active_search_query"] = search_query.strip()

    with col_theme:
        # Icon-only toggle button: switches theme between Light and Dark on click
        theme_icon = "☀️" if is_dark else "🌙"
        if st.button(theme_icon, key="btn_theme_toggle_icon", use_container_width=True, help="Switch Light/Dark Theme"):
            st.session_state["dark_mode"] = not is_dark
            st.rerun()

    with col_notify:
        with st.popover("Alerts", help="System Notifications", use_container_width=True):
            st.markdown("#### Notifications")
            st.markdown(
                """
                - Document queue ready for ingestion.
                - System operational and local storage connected.
                - Formula sanitization active on exports.
                """
            )
            if st.button("Mark all as read", key="btn_clear_notifs", use_container_width=True):
                st.toast("Notifications marked as read.")

    with col_user:
        with st.popover("Ragu Ram ▾", help="User Profile & Quick Settings", use_container_width=True):
            st.markdown("### Ragu Ram")
            st.caption("Final-Year AI & Data Science Student")
            st.caption("Role: Lead Software Engineer · Day 12 of 90")
            st.divider()
            if st.button("Open Settings & Preferences", key="btn_pop_settings", use_container_width=True):
                st.session_state["current_page"] = "Settings & Privacy"
                st.rerun()
            if st.button("View Workspace Dashboard", key="btn_pop_dash", use_container_width=True):
                st.session_state["current_page"] = "Workspace"
                st.rerun()
