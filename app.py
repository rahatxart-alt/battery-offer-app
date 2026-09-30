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

.sidebar-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--sap-dark);
}

/* Make sidebar radio look like navigation */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 3px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    padding: 9px 10px !important;
    border-radius: 5px;
    margin: 0 !important;
    color: #334e68;
    font-size: 13px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: #f1f5f8;
}

/* ---------- Top bar ---------- */
.topbar {
    height: 48px;
    background: #ffffff;
    border-bottom: 1px solid var(--sap-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    margin: -12px -8px 14px -8px;
}

.topbar-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.topbar-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--sap-dark);
}

.topbar-separator {
    color: #b7c1ca;
}

.topbar-section {
    font-size: 13px;
    color: var(--sap-muted);
}

.user-pill {
    background: #eef5fb;
    color: var(--sap-blue);
    border-radius: 14px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}

/* ---------- Page heading ---------- */
.breadcrumb {
    color: #74808c;
    font-size: 11px;
    margin-bottom: 2px;
}

.page-title {
    color: var(--sap-dark);
    font-size: 23px;
    line-height: 1.1;
    font-weight: 700;
    margin: 0;
}

.page-subtitle {
    color: var(--sap-muted);
    font-size: 12px;
    margin-top: 4px;
    margin-bottom: 14px;
}

/* ---------- Cards ---------- */
.sap-card {
    background: #ffffff;
    border: 1px solid var(--sap-border);
    border-radius: 6px;
    padding: 13px 15px;
    margin-bottom: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 9px;
}

.card-title {
    color: var(--sap-dark);
    font-size: 14px;
    font-weight: 700;
}

.card-meta {
    color: var(--sap-muted);
    font-size: 11px;
}

/* ---------- Customer info ---------- */
.customer-info {
    background: var(--sap-soft-blue);
    border: 1px solid #cfe2f6;
    border-left: 3px solid var(--sap-blue);
    border-radius: 4px;
    padding: 8px 11px;
    margin-top: 8px;
    color: #234b6f;
    font-size: 12px;
    line-height: 1.45;
}

.customer-info b {
    color: #0b4f88;
}

/* ---------- Streamlit controls ---------- */
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    font-size: 11px !important;
    color: #607080 !important;
    margin-bottom: 2px !important;
}

div[data-testid="stSelectbox"] > div > div,
div[data-testid="stNumberInput"] > div > div {
    min-height: 34px !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 34px !important;
    border-color: #c9d2dc !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}

div[data-testid="stNumberInput"] input {
    min-height: 34px !important;
    border-color: #c9d2dc !important;
    border-radius: 4px !important;
    font-size: 12px !important;
}

div[data-testid="stNumberInput"] button {
    min-height: 34px !important;
    width: 30px !important;
}

div[data-testid="stButton"] > button {
    min-height: 34px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

/* ---------- Item table header ---------- */
.table-head {
    display: grid;
    grid-template-columns: 48px 1.15fr 1.55fr 1fr 1fr 48px;
    gap: 8px;
    background: #f3f6f8;
    border: 1px solid #dce2e7;
    border-radius: 4px 4px 0 0;
    padding: 7px 9px;
    margin-top: 4px;
    color: #526372;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}

.table-head > div {
    display: flex;
    align-items: center;
}

/* ---------- Footer action bar ---------- */
.action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: rgba(255,255,255,0.98);
    border-top: 1px solid var(--sap-border);
    box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
    padding: 8px 22px;
}

.action-inner {
    max-width: 1500px;
    margin: 0 auto;
}

/* ---------- Small status ---------- */
.status-dot {
    width: 7px;
    height: 7px;
    background: var(--sap-green);
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}

.help-text {
    color: #758391;
    font-size: 10px;
}

/* ---------- Hide unnecessary Streamlit chrome ---------- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================
@st.cache_data
def load_data():
    try:
        data_file = Path("Data.xlsx")
        if not data_file.exists():
            st.error("Data.xlsx file paowa jayni. App-er sathe Data.xlsx rakhun.")
            return None, None

        df_cust = pd.read_excel(data_file, sheet_name="Customer", header=1)
        df_price = pd.read_excel(data_file, sheet_name="Price", header=1)
        return df_cust, df_price
    except Exception as e:
        st.error(f"Excel data load korte somossa hocche: {e}")
        return None, None


def clean_num(val):
    try:
        if pd.isna(val):
            return 0.0
        return float(str(val).replace(",", "").strip())
    except Exception:
        return 0.0


def clean_val(val, default=""):
    try:
        if pd.isna(val):
            return default
        value = str(val).strip()
        return value if value else default
    except Exception:
        return default


def add_row():
    st.session_state.rows.append({"id": st.session_state.row_id_counter})
    st.session_state.row_id_counter += 1


def delete_row(idx):
    if len(st.session_state.rows) > 1:
        st.session_state.rows.pop(idx)
    else:
        st.warning("At least one item row is required.")


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">P</div>
            <div class="sidebar-title">Procurement Pro</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_page = st.radio(
        "Navigation",
        [
            "📄 New Quotation",
            "📋 Quotation List",
            "👥 Customers",
            "📦 Products",
            "📊 Reports",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="help-text"><span class="status-dot"></span>System Online</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# LOAD / PREPARE DATA
# ============================================================
df_cust, df_price = load_data()

if df_cust is None or df_price is None:
    st.stop()

df_cust.columns = df_cust.columns.astype(str).str.strip()
df_price.columns = df_price.columns.astype(str).str.strip()

df_cust = df_cust.loc[:, ~df_cust.columns.str.contains("^Unnamed")]
df_price = df_price.loc[:, ~df_price.columns.str.contains("^Unnamed")]

cust_col = (
    "Customer Name"
    if "Customer Name" in df_cust.columns
    else df_cust.columns[0]
)
brand_col = (
    "Brand"
    if "Brand" in df_price.columns
    else df_price.columns[0]
)
type_col = (
    "Type"
    if "Type" in df_price.columns
    else df_price.columns[1]
)

df_cust = df_cust.dropna(subset=[cust_col]).copy()
df_price = df_price.dropna(subset=[brand_col, type_col]).copy()

df_cust[cust_col] = df_cust[cust_col].astype(str).str.strip()
df_price[brand_col] = df_price[brand_col].astype(str).str.strip()
df_price[type_col] = df_price[type_col].astype(str).str.strip()

# ============================================================
# OTHER PAGES - KEEP SIMPLE / READY FOR FUTURE MODULES
# ============================================================
if selected_page != "📄 New Quotation":
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-left">
                <span class="topbar-title">Procurement Pro</span>
                <span class="topbar-separator">/</span>
                <span class="topbar-section">Business Operations</span>
            </div>
            <span class="user-pill">AK</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="page-title">{selected_page}</h1>',
        unsafe_allow_html=True,
    )
    st.info(
        "This module is ready for expansion. The redesigned quotation workspace is available under New Quotation."
    )
    st.stop()

# ============================================================
# TOP BAR + PAGE HEADER
# ============================================================
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <span class="topbar-title">Procurement Pro</span>
            <span class="topbar-separator">/</span>
            <span class="topbar-section">Sales & Procurement</span>
        </div>
        <span class="user-pill">B2B Sales</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="breadcrumb">Home &nbsp;›&nbsp; Quotations &nbsp;›&nbsp; New Quotation</div>
    <h1 class="page-title">New Quotation</h1>
    <div class="page-subtitle">Create a customer price offer and generate a professional PDF.</div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# CUSTOMER CARD
# ============================================================
st.markdown('<div class="sap-card">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="card-header">
        <div class="card-title">Customer</div>
        <div class="card-meta">Required information</div>
    </div>
    """,
    unsafe_allow_html=True,
)

customer_list = sorted(df_cust[cust_col].unique().tolist())
selected_customer = st.selectbox(
    "Customer",
    options=customer_list,
    label_visibility="visible",
)

cust_matches = df_cust[df_cust[cust_col] == selected_customer]
if cust_matches.empty:
    st.error("Selected customer paowa jayni.")
    st.stop()

cust_row = cust_matches.iloc[0]
c_name = clean_val(cust_row.get("Customer Name", selected_customer), selected_customer)
c_attn = clean_val(cust_row.get("Concern Person", ""), "")
c_phone = clean_val(cust_row.get("Contact Number", ""), "")
c_addr = clean_val(cust_row.get("Company Address", ""), "")

st.markdown(
    f"""
    <div class="customer-info">
        <b>Customer Info</b>
        &nbsp; • &nbsp; Attn: <b>{c_attn or "—"}</b>
        &nbsp; • &nbsp; Phone: <b>{c_phone or "—"}</b>
        &nbsp; • &nbsp; Address: <b>{c_addr or "—"}</b>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SESSION STATE FOR ITEMS
# ============================================================
if "rows" not in st.session_state:
    st.session_state.rows = [{"id": 0}]
    st.session_state.row_id_counter = 1

# ============================================================
# QUOTATION ITEMS CARD
# ============================================================
st.markdown('<div class="sap-card">', unsafe_allow_html=True)

head_left, head_right = st.columns([7, 1.25], vertical_alignment="center")
with head_left:
    st.markdown(
        """
        <div class="card-header" style="margin-bottom:0;">
            <div class="card-title">Quotation Items</div>
            <div class="card-meta">Select products and adjust prices</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with head_right:
    if st.button("＋ Add Row", type="secondary", use_container_width=True):
        add_row()
        st.rerun()

st.markdown(
    """
    <div class="table-head">
        <div>S/N</div>
        <div>Brand *</div>
        <div>Product Type *</div>
        <div>MRP *</div>
        <div>DP *</div>
        <div>Action</div>
    </div>
    """,
    unsafe_allow_html=True,
)

brand_list = sorted(df_price[brand_col].unique().tolist())
selected_items = []

# ============================================================
# ITEM ROWS
# ============================================================
for idx, row_dict in enumerate(st.session_state.rows):
    row_id = row_dict["id"]

    r_cols = st.columns(
        [0.48, 2.25, 3.05, 1.55, 1.55, 0.55],
        vertical_alignment="center",
    )

    with r_cols[0]:
        st.markdown(
            f"""
            <div style="
                height:34px;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#526372;
                font-size:12px;
                font-weight:700;
                border-left:1px solid #dce2e7;
                border-bottom:1px solid #dce2e7;
                border-right:1px solid #dce2e7;
            ">{idx + 1}</div>
            """,
            unsafe_allow_html=True,
        )

    with r_cols[1]:
        b_brand = st.selectbox(
            f"Brand #{idx + 1}",
            options=brand_list,
            key=f"brand_{row_id}",
            label_visibility="collapsed",
        )

    filtered_bats = df_price[df_price[brand_col] == b_brand]
    bat_types = sorted(filtered_bats[type_col].unique().tolist())

    with r_cols[2]:
        b_type = st.selectbox(
            f"Type #{idx + 1}",
            options=bat_types,
            key=f"type_{row_id}",
            label_visibility="collapsed",
        )

    row_matches = filtered_bats[filtered_bats[type_col] == b_type]
    if row_matches.empty:
        continue

    row_data = row_matches.iloc[0]

    prev_key = f"prev_sel_{row_id}"
    curr_sel = f"{b_brand}_{b_type}"

    def_retail = clean_num(row_data.get("Retail price with VAT", 0))
    def_special = clean_num(
        row_data.get("Special Offer With VAT", def_retail)
    )
    if def_special == 0:
        def_special = def_retail

    if st.session_state.get(prev_key) != curr_sel:
        st.session_state[prev_key] = curr_sel
        st.session_state[f"ret_{row_id}"] = def_retail
        st.session_state[f"sp_{row_id}"] = def_special

    with r_cols[3]:
        c_retail = st.number_input(
            f"MRP #{idx + 1}",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key=f"ret_{row_id}",
            label_visibility="collapsed",
        )

    with r_cols[4]:
        c_special = st.number_input(
            f"DP #{idx + 1}",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            key=f"sp_{row_id}",
            label_visibility="collapsed",
        )

    with r_cols[5]:
        if st.button(
            "🗑",
            key=f"del_{row_id}",
            help="Delete row",
            use_container_width=True,
        ):
            delete_row(idx)
            st.rerun()

    calc_offer_wo_vat = c_special / 1.15
    calc_vat = c_special - calc_offer_wo_vat

    selected_items.append(
        {
            "Brand": b_brand,
            "Type": b_type,
            "Post": clean_val(row_data.get("Post", "I"), "I"),
            "Volt": clean_val(row_data.get("Volt", "12"), "12"),
            "AH": clean_val(row_data.get("AH", ""), ""),
            "Plate": clean_val(row_data.get("Plate", "N/A"), "N/A"),
            "Type_Sub": clean_val(
                row_data.get("Type.1", row_data.get("Type", "SMF")),
                "SMF",
            ),
            "Warranty": clean_val(row_data.get("Warranty", "24M"), "24M"),
            "Retail": f"{c_retail:,.2f}",
            "Offer_WO_VAT": f"{calc_offer_wo_vat:,.2f}",
            "VAT": f"{calc_vat:,.2f}",
            "Special": f"{c_special:,.2f}",
        }
    )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PDF GENERATOR
# ============================================================
def build_offer_pdf():
    current_date = datetime.date.today().strftime("%d-%b-%Y")
    ref_no = (
        f"RBL/CS/ACI/26-27/"
        f"{datetime.date.today().strftime('%d%m%y')}"
    )

    buffer = io.BytesIO()

    # Landscape A4 gives enough width for the detailed offer table.
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#B22222"),
        spaceAfter=4,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=normal_style,
        fontSize=6.5,
        leading=8,
        alignment=TA_CENTER,
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=small_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    elements = []

    elements.append(
        Paragraph(
            "<b>RAHIMAFROOZ BATTERIES LIMITED</b>",
            title_style,
        )
    )
    elements.append(
        Paragraph(
            "Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215 | "
            "Tel: 02-9113696",
            normal_style,
        )
    )
    elements.append(Spacer(1, 7))

    meta_data = [
        [
            Paragraph(f"<b>Ref:</b> {ref_no}", normal_style),
            Paragraph(f"<b>Date:</b> {current_date}", normal_style),
        ]
    ]

    meta_table = Table(meta_data, colWidths=[350, 350])
    meta_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(meta_table)
    elements.append(Spacer(1, 7))

    to_address = (
        f"<b>To:</b><br/>"
        f"<b>{c_name}</b><br/>"
        f"<b>Attn:</b> {c_attn} (Mob: {c_phone})<br/>"
        f"{c_addr}"
    )
    elements.append(Paragraph(to_address, normal_style))
    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            "<b>Subject: Price offer for supplying Rahimafrooz battery.</b>",
            normal_style,
        )
    )
    elements.append(
        Paragraph(
            "Dear Sir, Greetings!<br/>"
            "In reference to your mail, please find price offer & warranty "
            "terms for Rahimafrooz battery to serve your requirement.",
            normal_style,
        )
    )
    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph("<b>Price Offer Summary:</b>", normal_style)
    )
    elements.append(Spacer(1, 4))

    headers = [
        "Brand",
        "Type",
        "Post",
        "Volt",
        "AH",
        "Plate",
        "Type",
        "Warranty",
        "Retail Price w/ VAT",
        "Offer Without VAT",
        "VAT (15%)",
        "Special Offer With VAT",
    ]

    table_data = [
        [Paragraph(h, header_style) for h in headers]
    ]

    for item in selected_items:
        table_data.append(
            [
                Paragraph(str(item["Brand"]), small_style),
                Paragraph(str(item["Type"]), small_style),
                Paragraph(str(item["Post"]), small_style),
                Paragraph(str(item["Volt"]), small_style),
                Paragraph(str(item["AH"]), small_style),
                Paragraph(str(item["Plate"]), small_style),
                Paragraph(str(item["Type_Sub"]), small_style),
                Paragraph(str(item["Warranty"]), small_style),
                Paragraph(str(item["Retail"]), small_style),
                Paragraph(str(item["Offer_WO_VAT"]), small_style),
                Paragraph(str(item["VAT"]), small_style),
                Paragraph(str(item["Special"]), small_style),
            ]
        )

    # Total = 788 pt, safely inside landscape A4 after margins.
    col_widths = [
        64, 82, 34, 30, 36, 40, 44, 48,
        82, 82, 62, 84
    ]

    offer_table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1,
    )

    offer_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A6ED1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AAB4BE")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#F7F9FB"),
                ]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    elements.append(offer_table)
    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph("<b>Terms & Conditions:</b>", normal_style)
    )

    terms_text = """
    • <b>Price Validity:</b> 15 Days.<br/>
    • <b>Warranty:</b> As per manufacturer standard terms from date of delivery.<br/>
    • <b>Delivery Lead Time:</b> 15 days from PO issuance.<br/>
    • <b>Delivery Place:</b> At your warehouse.<br/>
    • <b>Payment Terms:</b> 15 Days from bill submission.<br/>
    • <b>VAT/TAX:</b> Rahimafrooz will provide Mushok 6.3. AIT deductible as per NBR rule.
    """

    elements.append(Paragraph(terms_text, normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Best Regards,", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            "<b>Md. Kamrul Islam</b><br/>"
            "Manager, B2B Sales<br/>"
            "Rahimafrooz Batteries Ltd<br/>"
            "Contact: +8801819466163",
            normal_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer, ref_no


# ============================================================
# FIXED BOTTOM ACTION BAR
# ============================================================
st.markdown('<div class="action-bar"><div class="action-inner">', unsafe_allow_html=True)

foot_cols = st.columns([2.2, 5.5, 3], vertical_alignment="center")

with foot_cols[0]:
    st.markdown(
        f"""
        <div style="font-size:12px;color:#526372;padding-top:5px;">
            <b>{len(selected_items)}</b> item(s)
            &nbsp;•&nbsp; Customer: <b>{c_name}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

with foot_cols[2]:
    generate_pdf = st.button(
        "📄  Generate Professional PDF Offer",
        type="primary",
        use_container_width=True,
    )

st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================
# GENERATE / DOWNLOAD
# ============================================================
if generate_pdf:
    if not selected_items:
        st.error("At least one quotation item is required.")
    else:
        pdf_buffer, ref_no = build_offer_pdf()

        st.success(
            f"Professional PDF ready — Reference: {ref_no}"
        )

        st.download_button(
            label="⬇ Download PDF Offer",
            data=pdf_buffer,
            file_name=f"Price_Offer_{c_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=False,
        )
