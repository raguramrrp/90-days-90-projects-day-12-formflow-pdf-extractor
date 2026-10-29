"""Theme and styling configuration for FormFlow matching the reference design."""

from __future__ import annotations

import streamlit as st


def get_theme_css(dark_mode: bool = False) -> str:
    """Generate comprehensive CSS for the high-end enterprise SaaS layout with flawless light/dark contrast."""
    if dark_mode:
        vars_css = """
        :root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            --text-color: #F8FAFC !important;
            --background-color: #0B132B !important;
            --secondary-background-color: #182343 !important;
            --primary-color: #3B82F6 !important;

            --ff-bg-main: #0B132B;
            --ff-bg-surface: #131E3A;
            --ff-bg-card: #182343;
            --ff-bg-subtle: #101932;
            --ff-text-primary: #F8FAFC;
            --ff-text-secondary: #CBD5E1;
            --ff-text-muted: #94A3B8;
            --ff-border: #283759;
            --ff-accent: #3B82F6;
            --ff-accent-hover: #60A5FA;
            --ff-accent-light: #1E3A8A;
            --ff-sidebar-bg: #0F172A;
            --ff-input-bg: #182343;
            --ff-hero-grad: linear-gradient(135deg, #1E3A8A 0%, #131E3A 85%);
            --ff-promo-grad: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            --ff-promo-title: #93C5FD;
            --ff-promo-sub: #60A5FA;
        }
        """
    else:
        vars_css = """
        :root, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            --text-color: #172B4D !important;
            --background-color: #F5F8FC !important;
            --secondary-background-color: #FFFFFF !important;
            --primary-color: #2563EB !important;

            --ff-bg-main: #F5F8FC;
            --ff-bg-surface: #FFFFFF;
            --ff-bg-card: #FFFFFF;
            --ff-bg-subtle: #F8FAFC;
            --ff-text-primary: #172B4D;
            --ff-text-secondary: #64748B;
            --ff-text-muted: #94A3B8;
            --ff-border: #E2E8F0;
            --ff-accent: #2563EB;
            --ff-accent-hover: #1D4ED8;
            --ff-accent-light: #EFF6FF;
            --ff-sidebar-bg: #F9FBFE;
            --ff-input-bg: #FFFFFF;
            --ff-hero-grad: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 85%);
            --ff-promo-grad: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            --ff-promo-title: #1E3A8A;
            --ff-promo-sub: #3B82F6;
        }
        """

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        {vars_css}

        /* Global reset and typography */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        }}
        
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"] {{
            background-color: var(--ff-bg-main) !important;
            color: var(--ff-text-primary) !important;
        }}

        /* Universal high-contrast text rules for both Light and Dark modes */
        .stApp,
        .stApp p,
        .stApp label,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] span {{
            color: var(--ff-text-primary) !important;
        }}

        /* Preserve specialized pills and badges from being turned pure white */
        .stApp span:not([class*="ff-status-"]):not([class*="ff-hero-pill"]) {{
            color: var(--ff-text-primary);
        }}

        .stCaption,
        .stCaption p,
        [data-testid="stCaptionContainer"] p,
        [data-testid="stCaptionContainer"] span,
        small {{
            color: var(--ff-text-secondary) !important;
        }}
        label[data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] {{
            color: var(--ff-text-primary) !important;
            font-weight: 500 !important;
        }}

        /* Hide Streamlit default chrome header/footer */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
            height: 0px !important;
        }}
        footer {{
            display: none !important;
        }}
        .block-container {{
            padding-top: 1.0rem !important;
            padding-bottom: 2rem !important;
            max-width: 1400px !important;
        }}

        /* ====================================================================
           INPUTS, SELECTBOXES, TEXTAREAS
           ==================================================================== */
        input,
        textarea,
        div[data-testid="stTextInput"] input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input,
        div[data-baseweb="textarea"] textarea {{
            background-color: var(--ff-input-bg) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 8px !important;
            color: var(--ff-text-primary) !important;
            font-size: 0.88rem !important;
        }}
        input::placeholder,
        textarea::placeholder {{
            color: var(--ff-text-secondary) !important;
            opacity: 0.8 !important;
        }}
        input:focus,
        textarea:focus {{
            border-color: var(--ff-accent) !important;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
        }}
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color: var(--ff-input-bg) !important;
            border: 1px solid var(--ff-border) !important;
            color: var(--ff-text-primary) !important;
            border-radius: 8px !important;
        }}
        [data-baseweb="select"] span,
        [data-baseweb="select"] div {{
            color: var(--ff-text-primary) !important;
        }}
        div[data-testid="stSelectbox"] svg {{
            fill: var(--ff-text-secondary) !important;
        }}
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [data-baseweb="menu"] ul,
        ul[role="listbox"] {{
            background-color: var(--ff-bg-card) !important;
            border: 1px solid var(--ff-border) !important;
        }}
        li[role="option"],
        [data-baseweb="menu"] li {{
            background-color: var(--ff-bg-card) !important;
            color: var(--ff-text-primary) !important;
        }}
        li[role="option"]:hover,
        [data-baseweb="menu"] li:hover,
        li[role="option"][aria-selected="true"] {{
            background-color: var(--ff-accent-light) !important;
            color: var(--ff-accent) !important;
        }}
        li[role="option"] * {{
            color: inherit !important;
        }}

        div[data-testid="stPopoverBody"] {{
            background-color: var(--ff-bg-card) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 10px !important;
            color: var(--ff-text-primary) !important;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
        }}
        div[data-testid="stPopoverBody"] * {{
            color: var(--ff-text-primary) !important;
        }}
        div[data-testid="stPopoverBody"] small,
        div[data-testid="stPopoverBody"] .stCaption {{
            color: var(--ff-text-secondary) !important;
        }}

        /* Checkboxes & Radios */
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] label span,
        [data-testid="stCheckbox"] label p,
        [data-testid="stRadio"] label,
        [data-testid="stRadio"] label span,
        [data-testid="stRadio"] label p,
        [data-testid="stRadio"] div[role="radiogroup"] label {{
            color: var(--ff-text-primary) !important;
        }}

        /* ====================================================================
           HERO HEADER SECTION
           ==================================================================== */
        .ff-hero-container {{
            background: var(--ff-hero-grad);
            border: 1px solid var(--ff-border);
            border-radius: 14px;
            padding: 22px 28px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(37, 99, 235, 0.04);
            position: relative;
            overflow: hidden;
        }}
        .ff-hero-left {{
            display: flex;
            align-items: flex-start;
            gap: 18px;
        }}
        .ff-hero-icon-box {{
            width: 52px;
            height: 52px;
            background-color: var(--ff-accent-light);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 4px;
        }}
        .ff-hero-pill {{
            display: inline-block;
            background-color: var(--ff-accent-light);
            color: {'#93C5FD' if dark_mode else '#2563EB'} !important;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 20px;
            margin-bottom: 6px;
            letter-spacing: 0.02em;
        }}
        .ff-hero-title {{
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--ff-text-primary) !important;
            margin: 0 0 6px 0;
            letter-spacing: -0.02em;
        }}
        .ff-hero-subtitle {{
            font-size: 0.90rem;
            color: var(--ff-text-secondary) !important;
            margin: 0;
            max-width: 620px;
            line-height: 1.45;
        }}
        .ff-hero-right {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }}

        /* ====================================================================
           KPI METRIC CARDS
           ==================================================================== */
        .ff-metric-card {{
            background-color: var(--ff-bg-card);
            border: 1px solid var(--ff-border);
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            margin-bottom: 16px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .ff-metric-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
        }}
        .ff-metric-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .ff-metric-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .ff-metric-label-group {{
            flex-grow: 1;
            margin-left: 12px;
        }}
        .ff-metric-label {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--ff-text-secondary) !important;
            font-weight: 600;
        }}
        .ff-metric-chevron {{
            color: var(--ff-text-secondary);
            display: flex;
            align-items: center;
        }}
        .ff-metric-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--ff-text-primary) !important;
            margin-bottom: 2px;
            line-height: 1.2;
        }}
        .ff-metric-subtext {{
            font-size: 0.76rem;
            color: var(--ff-text-secondary) !important;
        }}

        /* ====================================================================
           PANELS & DROPZONE
           ==================================================================== */
        .ff-panel-header {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 16px;
        }}
        .ff-panel-header-icon {{
            width: 36px;
            height: 36px;
            background-color: var(--ff-accent-light);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .ff-panel-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--ff-text-primary) !important;
            margin: 0;
            line-height: 1.3;
        }}
        .ff-panel-subtitle {{
            font-size: 0.80rem;
            color: var(--ff-text-secondary) !important;
            margin: 2px 0 0 0;
        }}

        /* Drag & Drop Area */
        .ff-dropzone {{
            border: 2px dashed var(--ff-border);
            background-color: var(--ff-bg-subtle);
            border-radius: 10px;
            padding: 22px 18px;
            text-align: center;
            margin-bottom: 16px;
            transition: border-color 0.15s ease;
        }}
        .ff-dropzone:hover {{
            border-color: var(--ff-accent);
        }}
        .ff-dropzone-cloud {{
            width: 44px;
            height: 44px;
            background-color: var(--ff-accent-light);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px auto;
        }}
        .ff-dropzone-text {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--ff-text-primary) !important;
            margin-bottom: 4px;
        }}
        .ff-dropzone-or {{
            font-size: 0.78rem;
            color: var(--ff-text-secondary) !important;
            margin-bottom: 6px;
        }}
        .ff-dropzone-info {{
            font-size: 0.72rem;
            color: var(--ff-text-secondary) !important;
            margin-top: 8px;
        }}

        /* ====================================================================
           STATUS BADGES & PILLS
           ==================================================================== */
        .ff-status-pill {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 6px;
            letter-spacing: 0.02em;
        }}
        .stApp .ff-status-valid, .stApp .ff-status-completed {{
            background-color: {'#064E3B' if dark_mode else '#ECFDF5'} !important;
            color: {'#6EE7B7' if dark_mode else '#059669'} !important;
            border: 1px solid {'#047857' if dark_mode else '#A7F3D0'} !important;
        }}
        .stApp .ff-status-warning, .stApp .ff-status-completed-warnings {{
            background-color: {'#78350F' if dark_mode else '#FFFBEB'} !important;
            color: {'#FCD34D' if dark_mode else '#D97706'} !important;
            border: 1px solid {'#B45309' if dark_mode else '#FDE68A'} !important;
        }}
        .stApp .ff-status-invalid, .stApp .ff-status-review, .stApp .ff-status-failed {{
            background-color: {'#7F1D1D' if dark_mode else '#FEF2F2'} !important;
            color: {'#FCA5A5' if dark_mode else '#DC2626'} !important;
            border: 1px solid {'#B91C1C' if dark_mode else '#FECACA'} !important;
        }}
        .stApp .ff-status-missing {{
            background-color: var(--ff-bg-subtle) !important;
            color: var(--ff-text-secondary) !important;
            border: 1px solid var(--ff-border) !important;
        }}
        .stApp .ff-status-unverified, .stApp .ff-status-processing, .stApp .ff-status-pending {{
            background-color: var(--ff-accent-light) !important;
            color: {'#93C5FD' if dark_mode else '#2563EB'} !important;
            border: 1px solid {'#3B82F6' if dark_mode else '#BFDBFE'} !important;
        }}
        .stApp .ff-status-corrected {{
            background-color: {'#581C87' if dark_mode else '#F3E8FF'} !important;
            color: {'#D8B4FE' if dark_mode else '#7E22CE'} !important;
            border: 1px solid {'#7E22CE' if dark_mode else '#E9D5FF'} !important;
        }}

        /* ====================================================================
           SIDEBAR STYLING & NAVIGATION
           ==================================================================== */
        section[data-testid="stSidebar"] {{
            background-color: var(--ff-sidebar-bg) !important;
            border-right: 1px solid var(--ff-border) !important;
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.0rem !important;
            padding-left: 1.0rem !important;
            padding-right: 1.0rem !important;
        }}
        section[data-testid="stSidebar"] button {{
            text-align: left !important;
            justify-content: flex-start !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
            box-shadow: none !important;
            height: auto !important;
            min-height: 38px !important;
        }}
        /* Active nav item */
        section[data-testid="stSidebar"] button[kind="primary"],
        section[data-testid="stSidebar"] [data-testid="baseButton-primary"],
        section[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{
            background-color: var(--ff-accent-light) !important;
            color: {'#93C5FD' if dark_mode else '#2563EB'} !important;
            font-weight: 600 !important;
            border: 1px solid {'#3B82F6' if dark_mode else '#BFDBFE'} !important;
        }}
        section[data-testid="stSidebar"] button[kind="primary"] * {{
            color: {'#93C5FD' if dark_mode else '#2563EB'} !important;
        }}
        /* Inactive nav item */
        section[data-testid="stSidebar"] button[kind="secondary"],
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"],
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {{
            background-color: transparent !important;
            color: var(--ff-text-secondary) !important;
            border: 1px solid transparent !important;
        }}
        section[data-testid="stSidebar"] button[kind="secondary"] * {{
            color: var(--ff-text-secondary) !important;
        }}
        section[data-testid="stSidebar"] button[kind="secondary"]:hover,
        section[data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover,
        section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {{
            background-color: var(--ff-bg-card) !important;
            color: var(--ff-text-primary) !important;
        }}
        section[data-testid="stSidebar"] button[kind="secondary"]:hover * {{
            color: var(--ff-text-primary) !important;
        }}

        /* Sidebar Brand & Header */
        .ff-sidebar-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .ff-sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .ff-sidebar-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--ff-text-primary) !important;
            letter-spacing: -0.02em;
        }}
        .ff-sidebar-subtitle {{
            font-size: 0.74rem;
            color: var(--ff-text-secondary) !important;
            margin-top: 2px;
        }}

        /* Sidebar Cards */
        .ff-sidebar-card {{
            background-color: var(--ff-bg-card);
            border: 1px solid var(--ff-border);
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }}
        .ff-sidebar-card-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--ff-text-secondary) !important;
            letter-spacing: 0.04em;
            margin-bottom: 3px;
        }}
        .ff-sidebar-card-title {{
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--ff-text-primary) !important;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .ff-sidebar-promo {{
            background: var(--ff-promo-grad);
            border: 1px solid var(--ff-border);
            border-radius: 12px;
            padding: 14px 14px;
            margin-top: 14px;
            position: relative;
            overflow: hidden;
        }}
        .ff-sidebar-promo-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--ff-promo-title) !important;
            margin: 0 0 4px 0;
        }}
        .ff-sidebar-promo-sub {{
            font-size: 0.72rem;
            color: var(--ff-promo-sub) !important;
            margin: 0;
            font-weight: 500;
        }}

        /* ====================================================================
           UNIVERSAL BUTTON STYLING
           ==================================================================== */
        .stButton > button:not([kind="primary"]),
        button[kind="secondary"],
        [data-testid*="BaseButton-secondary"],
        [data-testid*="baseButton-secondary"],
        div[data-testid="stFileUploaderDropzone"] button {{
            background-color: var(--ff-bg-card) !important;
            color: var(--ff-text-primary) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
        }}
        .stButton > button:not([kind="primary"]):hover,
        button[kind="secondary"]:hover,
        [data-testid*="BaseButton-secondary"]:hover,
        [data-testid*="baseButton-secondary"]:hover {{
            background-color: var(--ff-accent-light) !important;
            border-color: var(--ff-accent) !important;
            color: var(--ff-accent) !important;
        }}
        .stButton > button:not([kind="primary"]) *,
        button[kind="secondary"] *,
        [data-testid*="BaseButton-secondary"] *,
        [data-testid*="baseButton-secondary"] * {{
            color: inherit !important;
        }}

        /* Tooltip & Help Icons: Clear, sharp, and high-contrast in both Light and Dark themes */
        [data-testid*="TooltipHoverTarget"],
        [data-testid*="TooltipIcon"],
        [data-testid="stTooltipHoverTarget"],
        [data-testid="stTooltipIcon"],
        div[data-testid*="Tooltip"] button,
        div[data-testid*="tooltip"] button,
        .stTooltipIcon,
        .stTooltipHoverTarget {{
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 4px !important;
            margin: 0 !important;
            min-height: unset !important;
            height: auto !important;
            width: auto !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            opacity: 1 !important;
        }}
        [data-testid*="TooltipHoverTarget"] svg,
        [data-testid*="TooltipIcon"] svg,
        div[data-testid*="Tooltip"] button svg,
        div[data-testid*="tooltip"] button svg,
        .stTooltipIcon svg,
        .stTooltipHoverTarget svg {{
            color: var(--ff-accent) !important;
            fill: currentColor !important;
            stroke: none !important;
            width: 15px !important;
            height: 15px !important;
            opacity: 0.85 !important;
        }}
        [data-testid*="TooltipHoverTarget"]:hover svg,
        [data-testid*="TooltipIcon"]:hover svg,
        div[data-testid*="Tooltip"] button:hover svg {{
            color: var(--ff-accent-hover) !important;
            fill: currentColor !important;
            stroke: none !important;
            opacity: 1.0 !important;
        }}

        button[kind="primary"],
        [data-testid*="BaseButton-primary"],
        [data-testid*="baseButton-primary"],
        .stButton > button[kind="primary"],
        [data-testid="stDownloadButton"] > button {{
            background-color: var(--ff-accent) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 0.90rem !important;
            box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
            transition: background-color 0.15s ease !important;
        }}
        button[kind="primary"]:hover,
        [data-testid*="BaseButton-primary"]:hover,
        [data-testid*="baseButton-primary"]:hover,
        .stButton > button[kind="primary"]:hover,
        [data-testid="stDownloadButton"] > button:hover {{
            background-color: var(--ff-accent-hover) !important;
            color: #FFFFFF !important;
        }}
        button[kind="primary"] *,
        [data-testid*="BaseButton-primary"] *,
        [data-testid*="baseButton-primary"] *,
        .stButton > button[kind="primary"] *,
        [data-testid="stDownloadButton"] > button * {{
            color: #FFFFFF !important;
        }}

        /* File Uploader styling */
        [data-testid="stFileUploader"],
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploaderDropzone"] > div {{
            background-color: var(--ff-bg-card) !important;
            border: 1px dashed var(--ff-border) !important;
            border-radius: 10px !important;
        }}
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stFileUploaderDropzone"] div {{
            color: var(--ff-text-secondary) !important;
        }}
        [data-testid="stFileUploaderDropzone"] button {{
            background-color: var(--ff-bg-subtle) !important;
            color: var(--ff-text-primary) !important;
            border: 1px solid var(--ff-border) !important;
        }}
        [data-testid="stFileUploaderDropzone"] button * {{
            color: var(--ff-text-primary) !important;
        }}

        /* Expanders */
        [data-testid="stExpander"],
        details[data-testid="stExpander"] {{
            background-color: var(--ff-bg-card) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 8px !important;
        }}
        summary[data-testid="stExpanderSummary"],
        summary[data-testid="stExpanderSummary"] * {{
            color: var(--ff-text-primary) !important;
        }}
        summary[data-testid="stExpanderSummary"] svg {{
            fill: var(--ff-text-primary) !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: var(--ff-bg-card) !important;
            color: var(--ff-text-primary) !important;
        }}

        /* Tabs styling */
        [data-baseweb="tab-list"] {{
            background-color: transparent !important;
            border-bottom: 1px solid var(--ff-border) !important;
            gap: 8px !important;
        }}
        [data-baseweb="tab"],
        button[role="tab"] {{
            color: var(--ff-text-secondary) !important;
            background-color: transparent !important;
            border-radius: 6px 6px 0 0 !important;
            padding: 8px 16px !important;
            font-size: 0.88rem !important;
            border: none !important;
        }}
        [data-baseweb="tab"][aria-selected="true"],
        button[role="tab"][aria-selected="true"] {{
            color: var(--ff-accent) !important;
            border-bottom: 2px solid var(--ff-accent) !important;
            font-weight: 600 !important;
            background-color: var(--ff-accent-light) !important;
        }}
        [data-baseweb="tab"] *,
        button[role="tab"] * {{
            color: inherit !important;
        }}

        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: var(--ff-text-primary) !important;
            font-weight: 700 !important;
        }}
        [data-testid="stMetricLabel"] p {{
            color: var(--ff-text-secondary) !important;
            font-weight: 500 !important;
            font-size: 0.80rem !important;
        }}

        /* Alerts */
        [data-testid="stAlert"] {{
            border-radius: 8px !important;
        }}
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] div,
        [data-testid="stAlert"] span {{
            color: var(--ff-text-primary) !important;
        }}

        /* Tables & Code */
        [data-testid="stTable"] table {{
            background-color: var(--ff-bg-card) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 8px !important;
        }}
        [data-testid="stTable"] th {{
            background-color: var(--ff-bg-subtle) !important;
            color: var(--ff-text-primary) !important;
            font-weight: 600 !important;
            border-bottom: 1px solid var(--ff-border) !important;
        }}
        [data-testid="stTable"] td {{
            color: var(--ff-text-primary) !important;
            border-bottom: 1px solid var(--ff-border) !important;
        }}
        code, pre, pre code {{
            background-color: var(--ff-bg-subtle) !important;
            color: var(--ff-text-primary) !important;
            border: 1px solid var(--ff-border) !important;
            border-radius: 6px !important;
        }}
    </style>
    """


def inject_theme() -> None:
    """Inject CSS according to the session state theme preference."""
    dark_mode = st.session_state.get("dark_mode", False)
    st.markdown(get_theme_css(dark_mode), unsafe_allow_html=True)
