import io
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="Procurement Pro - Price Offer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PROFESSIONAL SAP / FIORI-STYLE UI
# ============================================================
st.markdown(
    """
<style>
/* ---------- Global ---------- */
:root {
    --sap-blue: #0a6ed1;
    --sap-dark: #12344d;
    --sap-navy: #0b2f4a;
    --sap-bg: #f5f7f9;
    --sap-border: #d8dee5;
    --sap-text: #1d2d3e;
    --sap-muted: #6a7785;
    --sap-soft-blue: #eaf3fc;
    --sap-green: #107e3e;
    --sap-red: #bb0000;
}

.stApp {
    background: var(--sap-bg);
    color: var(--sap-text);
}

/* Reduce Streamlit's default huge top spacing */
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 5rem !important;
    max-width: 1500px !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--sap-border);
}

section[data-testid="stSidebar"] > div {
    padding-top: 0.8rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 8px 14px 8px;
    border-bottom: 1px solid #edf0f2;
    margin-bottom: 12px;
}

.sidebar-logo {
    width: 34px;
    height: 34px;
    border-radius: 7px;
    background: var(--sap-blue);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
    font-weight: 700;
}
