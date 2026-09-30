import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

st.set_page_config(page_title="Procurement Pro - Rahimafrooz Offer Generator", layout="wide")

# Custom CSS for Professional Procurement Pro Dashboard Styling
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
    }
    .dashboard-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation matching the design
with st.sidebar:
    st.markdown("### 📦 **Procurement Pro**")
    st.markdown("---")
    selected_page = st.radio(
        "Navigation", 
        ["📄 New Quotation", "📋 Quotation List", "👥 Customers", "📦 Products", "📊 Reports"],
        label_visibility="collapsed"
    )

@st.cache_data
def load_data():
    try:
        df_cust = pd.read_excel('Data.xlsx', sheet_name='Customer', header=1)
        df_price = pd.read_excel('Data.xlsx', sheet_name='Price', header=1)
        return df_cust, df_price
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return None, None

df_cust, df_price = load_data()

if df_cust is None or df_price is None:
    st.error("Data.xlsx file read korte somoshya hocche.")
else:
    df_cust.columns = df_cust.columns.astype(str).str.strip()
    df_price.columns = df_price.columns.astype(str).str.strip()
    
    df_cust = df_cust.loc[:, ~df_cust.columns.str.contains('^Unnamed')]
    df_price = df_price.loc[:, ~df_price.columns.str.contains('^Unnamed')]
    
    cust_col = 'Customer Name' if 'Customer Name' in df_cust.columns else df_cust.columns[0]
    brand_col = 'Brand' if 'Brand' in df_price.columns else df_price.columns[0]
    type_col = 'Type' if 'Type' in df_price.columns else df_price.columns[1]
    
    df_cust = df_cust.dropna(subset=[cust_col])
    df_price = df_price.dropna(subset=[brand_col, type_col])
    
    df_cust[cust_col] = df_cust[cust_col].astype(str).str.strip()
    df_price[brand_col] = df_price[brand_col].astype(str).str.strip()
    df_price[type_col] = df_price[type_col].astype(str).str.strip()
    
    # Breadcrumbs & Title
    st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 0px;'>Home > Quotations > <b>New Quotation</b></p>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #0f172a; margin-top: 5px; margin-bottom: 20px;'>New Quotation</h2>", unsafe_allow_html=True)
    
    # Card 1: Select Customer
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight: 600; color: #1e293b; margin-bottom: 8px;'>Select Customer Name</p>", unsafe_allow_html=True)
    
    customer_list = sorted(df_cust[cust_col].unique().tolist())
    selected_customer = st.selectbox("Select Customer Name", options=customer_list, label_visibility="collapsed")
    
    cust_row = df_cust[df_cust[cust_col] == selected_customer].iloc[0]
    c_name = str(cust_row.get('Customer Name', ''))
    c_attn = str(cust_row.get('Concern Person', ''))
    c_phone = str(cust_row.get('Contact Number', ''))
    c_addr = str(cust_row.get('Company Address', ''))
    
    st.markdown(f"""
    <div style='background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; margin-top: 12px; color: #1e40af; font-size: 14px;'>
        <b>ℹ️ Customer Info:</b> Attn: <b>{c_attn}</b> &nbsp;|&nbsp; Phone: <b>{c_phone}</b> &nbsp;|&nbsp; Address: <b>{c_addr}</b>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Session state for dynamic rows and deletion support
    if 'rows' not in st.session_state:
        st.session_state.rows = [{'id': 0}]
        st.session_state.row_id_counter = 1

    def add_row():
        st.session_state.rows.append({'id': st.session_state.row_id_counter})
        st.session_state.row_id_counter += 1

    def delete_row(idx):
        if len(st.session_state.rows) > 1:
            st.session_state.rows.pop(idx)
        else:
            st.warning("At least one item row is required.")

    # Card 2: Quotation Items
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([6, 1])
    with col_t1:
        st.markdown("<h4 style='margin: 0; color: #1e293b; padding-top: 5px;'>Quotation Items</h4>", unsafe_allow_html=True)
    with col_t2:
        if st.button("＋ Add Row", type="secondary", use_container_width=True):
            add_row()
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table Header Row
    th_cols = st.columns([0.6, 2.5, 3, 1.8, 1.8, 0.8])
    with th_cols[0]: st.markdown("**S/N**")
    with th_cols[1]: st.markdown("**Brand \***")
    with th_cols[2]: st.markdown("**Type \***")
    with th_cols[3]: st.markdown("**MRP \***")
    with th_cols[4]: st.markdown("**DP \***")
    with th_cols[5]: st.markdown("**Actions**")
    
    st.markdown("<hr style='margin: 5px 0 10px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    brand_list = sorted(df_price[brand_col].unique().tolist())
    selected_items = []

    def clean_num(val):
        try:
            return float(str(val).replace(',', '').strip())
        except:
            return 0.0

    def clean_val(val, default=""):
        try:
            if pd.isna(val):
                return default
            return str(val).strip()
        except:
            return default

    for idx, row_dict in enumerate(st.session_state.rows):
        r_cols = st.columns([0.6, 2.5, 3, 1.8, 1.8, 0.8])
        
        with r_cols[0]:
            st.markdown(f"<p style='padding-top: 8px; font-weight: 500; color: #475569;'>{idx+1}</p>", unsafe_allow_html=True)
            
        with r_cols[1]:
            b_brand = st.selectbox(f"Brand #{idx+1}", options=brand_list, key=f"brand_{row_dict['id']}", label_visibility="collapsed")
            
        filtered_bats = df_price[df_price[brand_col] == b_brand]
        bat_types = sorted(filtered_bats[type_col].unique().tolist())
        
        with r_cols[2]:
            b_type = st.selectbox(f"Type #{idx+1}", options=bat_types, key=f"type_{row_dict['id']}", label_visibility="collapsed")
            
        row_data = filtered_bats[filtered_bats[type_col] == b_type].iloc[0]
        
        prev_key = f"prev_sel_{row_dict['id']}"
        curr_sel = f"{b_brand}_{b_type}"
        
        def_retail = clean_num(row_data.get('Retail price with VAT', 0))
        def_special = clean_num(row_data.get('Special Offer With VAT', def_retail))
        if def_special == 0:
            def_special = def_retail

        if st.session_state.get(prev_key) != curr_sel:
            st.session_state[prev_key] = curr_sel
            st.session_state[f"ret_{row_dict['id']}"] = def_retail
            st.session_state[f"sp_{row_dict['id']}"] = def_special

        with r_cols[3]:
            c_retail = st.number_input(f"MRP #{idx+1}", step=100.0, key=f"ret_{row_dict['id']}", label_visibility="collapsed")
        with r_cols[4]:
            c_special = st.number_input(f"DP #{idx+1}", step=50.0, key=f"sp_{row_dict['id']}", label_visibility="collapsed")
            
        with r_cols[5]:
            if st.button("🗑️", key=f"del_{row_dict['id']}", help="Delete Row"):
                delete_row(idx)
                st.rerun()
                
        calc_offer_wo_vat = c_special / 1.15
        calc_vat = c_special - calc_offer_wo_vat
            
        selected_items.append({
            "Brand": b_brand,
            "Type": b_type,
            "Post": clean_val(row_data.get('Post', 'I'), 'I'),
            "Volt": clean_val(row_data.get('Volt', '12'), '12'),
            "AH": clean_val(row_data.get('AH', ''), ''),
            "Plate": clean_val(row_data.get('Plate', 'N/A'), 'N/A'),
            "Type_Sub": clean_val(row_data.get('Type.1', row_data.get('Type', 'SMF')), 'SMF'),
            "Warranty": clean_val(row_data.get('Warranty', '24M'), '24M'),
            "Retail": f"{c_retail:,.2f}",
            "Offer_WO_VAT": f"{calc_offer_wo_vat:,.2f}",
            "VAT": f"{calc_vat:,.2f}",
            "Special": f"{c_special:,.2f}"
        })

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer Section with Total Items and Generate PDF Button
    st.markdown("<hr style='margin: 30px 0 15px 0;'>", unsafe_allow_html=True)
    foot_cols = st.columns([2, 6, 4])
    with foot_cols[0]:
        st.markdown(f"<p style='color: #475569; font-weight: 500; padding-top: 8px;'>Total Items: {len(selected_items)}</p>", unsafe_allow_html=True)
    with foot_cols[2]:
        if st.button("🚀 Generate Professional PDF Offer", type="primary", use_container_width=True):
            if cust_row.empty:
                st.error("Nirbachito customer paowa jayni.")
            else:
                current_date = datetime.date.today().strftime("%d-%b-%Y")
                ref_no = f"RBL/CS/ACI/26-27/{datetime.date.today().strftime('%d%m%y')}"
                    
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
                elements = []
                
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor("#B22222"), spaceAfter=4)
                normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9.5, leading=13)

                elements.append(Paragraph("<b>RAHIMAFROOZ BATTERIES LIMITED</b>", title_style))
                elements.append(Paragraph("Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215 | Tel: 02-9113696", normal_style))
                elements.append(Spacer(1, 8))
                
                elements.append(Paragraph(f"<b>Ref:</b> {ref_no}", normal_style))
                elements.append(Paragraph(f"<b>Date:</b> {current_date}", normal_style))
                elements.append(Spacer(1, 8))
                
                to_address = f"<b>To:</b><br/><b>{c_name}</b><br/><b>Attn:</b> {c_attn} (Mob: {c_phone})<br/>{c_addr}"
                elements.append(Paragraph(to_address, normal_style))
                elements.append(Spacer(1, 10))
                
                elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
                elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", normal_style))
                elements.append(Spacer(1, 10))
                
                elements.append(Paragraph("<b>Price Offer Summary:</b>", styles['Heading4']))
                elements.append(Spacer(1, 4))
                
                table_data = [
                    ["Brand", "Type", "Post", "Volt", "AH", "Plate", "Type", "Warranty", "Retail Price w/ VAT", "Offer Without VAT", "VAT (15%)", "Special Offer With VAT"]
                ]
                
                for item in selected_items:
                    table_data.append([
                        item["Brand"], item["Type"], item["Post"], item["Volt"], item["AH"], 
                        item["Plate"], item["Type_Sub"], item["Warranty"], item["Retail"], 
                        item["Offer_WO_VAT"], item["VAT"], item["Special"]
                    ])
                
                t = Table(table_data, colWidths=[55, 75, 30, 25, 30, 32, 35, 40, 62, 62, 50, 68])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7.5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
                ]))
                
                elements.append(t)
                elements.append(Spacer(1, 12))
                
                elements.append(Paragraph("<b>Terms & Conditions:</b>", styles['Heading4']))
                terms_text = """
                • <b>Price Validity:</b> 15 Days.<br/>
                • <b>Warranty:</b> As per manufacturer standard terms from date of delivery.<br/>
                • <b>Delivery Lead Time:</b> 15 days from PO issuance.<br/>
                • <b>Delivery Place:</b> At your warehouse.<br/>
                • <b>Payment Terms:</b> 15 Days from bill submission.<br/>
                • <b>VAT/TAX:</b> Rahimafrooz will provide Mushok 6.3. AIT deductible as per NBR rule.
                """
                elements.append(Paragraph(terms_text, normal_style))
                elements.append(Spacer(1, 15))
                
                elements.append(Paragraph("Best Regards,", normal_style))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph("<b>Md. Kamrul Islam</b><br/>Manager, B2B Sales<br/>Rahimafrooz Batteries Ltd<br/>Contact: +8801819466163", normal_style))
                
                doc.build(elements)
                buffer.seek(0)
                
                st.success("Professional PDF successfully toiri hoyeche!")
                st.download_button(
                    label="📥 Download Professional PDF Offer",
                    data=buffer,
                    file_name=f"Price_Offer_{c_name.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
