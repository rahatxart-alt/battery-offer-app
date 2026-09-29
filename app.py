import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

st.set_page_config(page_title="Rahimafrooz Offer Generator", layout="centered")

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
    
    customer_list = sorted(df_cust[cust_col].unique().tolist())
    selected_customer = st.selectbox("Select Customer Name:", options=customer_list)
    
    if 'compact_items' not in st.session_state:
        st.session_state.compact_items = 1

    def add_row():
        st.session_state.compact_items += 1

    def remove_row():
        if st.session_state.compact_items > 1:
            st.session_state.compact_items -= 1

    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        st.button("➕ Add Row", on_click=add_row)
    with col_b2:
        if st.session_state.compact_items > 1:
            st.button("➖ Remove Row", on_click=remove_row)

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

    for i in range(st.session_state.compact_items):
        st.markdown(f"**Item #{i+1} Details:**")
        
        # 1-Column vertical stacked layout
        b_brand = st.selectbox(f"Brand #{i+1}", options=brand_list, key=f"c_brand_{i}")
        
        filtered_bats = df_price[df_price[brand_col] == b_brand]
        bat_types = sorted(filtered_bats[type_col].unique().tolist())
        
        b_type = st.selectbox(f"Type #{i+1}", options=bat_types, key=f"c_type_{i}")
            
        row_data = filtered_bats[filtered_bats[type_col] == b_type].iloc[0]
        
        def_post = clean_val(row_data.get('Post', 'I'), 'I')
        def_volt = clean_val(row_data.get('Volt', '12'), '12')
        def_ah = clean_val(row_data.get('AH', ''), '')
        def_plate = clean_val(row_data.get('Plate', 'N/A'), 'N/A')
        def_btype = clean_val(row_data.get('Type.1', row_data.get('Type', 'SMF')), 'SMF')
        def_warranty = clean_val(row_data.get('Warranty', '24M'), '24M')
        def_retail = clean_num(row_data.get('Retail price with VAT', 0))
        def_special = clean_num(row_data.get('Special Offer With VAT', def_retail))
        if def_special == 0:
            def_special = def_retail

        c_post = st.text_input(f"Post #{i+1}", value=def_post, key=f"post_{i}")
        c_volt = st.text_input(f"Volt #{i+1}", value=def_volt, key=f"volt_{i}")
        c_ah = st.text_input(f"AH #{i+1}", value=def_ah, key=f"ah_{i}")
        c_plate = st.text_input(f"Plate #{i+1}", value=def_plate, key=f"plate_{i}")
        c_btype = st.text_input(f"Type (SMF) #{i+1}", value=def_btype, key=f"btype_{i}")
        c_warranty = st.text_input(f"Warranty #{i+1}", value=def_warranty, key=f"warr_{i}")
        c_retail = st.number_input(f"Retail w/VAT #{i+1}", value=def_retail, step=100.0, key=f"ret_{i}")
        c_special = st.number_input(f"Special Offer (DP) #{i+1}", value=def_special, step=50.0, key=f"sp_{i}")
            
        selected_items.append({
            "Brand": b_brand,
            "Type": b_type,
            "Post": c_post,
            "Volt": c_volt,
            "AH": c_ah,
            "Plate": c_plate,
            "Type_Sub": c_btype,
            "Warranty": c_warranty,
            "Retail": f"{c_retail:,.2f}",
            "Offer_WO_VAT": str(row_data.get('Offer Without VAT', '')),
            "VAT": str(row_data.get('VAT (15%)', '')),
            "Special": f"{c_special:,.2f}"
        })
        st.markdown("---")

    if st.button("🚀 Generate Professional PDF Offer", type="primary"):
        cust_matches = df_cust[df_cust[cust_col] == selected_customer]
        
        if cust_matches.empty:
            st.error("Nirbachito customer paowa jayni.")
        else:
            cust_row = cust_matches.iloc[0]
                
            current_date = datetime.date.today().strftime("%d-%b-%Y")
            ref_no = f"RBL/CS/ACI/26-27/{datetime.date.today().strftime('%d%m%y')}"
                
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
            elements = []
            
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#B22222"), spaceAfter=4)
            normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14)

            elements.append(Paragraph("<b>RAHIMAFROOZ BATTERIES LIMITED</b>", title_style))
            elements.append(Paragraph("Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215 | Tel: 02-9113696", normal_style))
            elements.append(Spacer(1, 10))
            
            elements.append(Paragraph(f"<b>Ref:</b> {ref_no}", normal_style))
            elements.append(Paragraph(f"<b>Date:</b> {current_date}", normal_style))
            elements.append(Spacer(1, 10))
            
            cust_name = str(cust_row.get('Customer Name', ''))
            concern_person = str(cust_row.get('Concern Person', ''))
            contact_no = str(cust_row.get('Contact Number', ''))
            cust_address = str(cust_row.get('Company Address', ''))
            
            to_address = f"<b>To:</b><br/><b>{cust_name}</b><br/><b>Attn:</b> {concern_person} (Mob: {contact_no})<br/>{cust_address}"
            elements.append(Paragraph(to_address, normal_style))
            elements.append(Spacer(1, 12))
            
            elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
            elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", normal_style))
            elements.append(Spacer(1, 12))
            
            elements.append(Paragraph("<b>Price Offer Summary:</b>", styles['Heading4']))
            elements.append(Spacer(1, 5))
            
            table_data = [
                ["Brand", "Type", "Post", "Volt", "AH", "Plate", "Type", "Warranty", "Retail Price w/ VAT", "Offer Without VAT", "VAT (15%)", "Special Offer With VAT"]
            ]
            
            for item in selected_items:
                table_data.append([
                    item["Brand"], item["Type"], item["Post"], item["Volt"], item["AH"], 
                    item["Plate"], item["Type_Sub"], item["Warranty"], item["Retail"], 
                    item["Offer_WO_VAT"], item["VAT"], item["Special"]
                ])
            
            t = Table(table_data, colWidths=[65, 100, 35, 30, 35, 40, 45, 55, 75, 75, 60, 85])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 15))
            
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
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("Best Regards,", normal_style))
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Md. Kamrul Islam</b><br/>Manager, B2B Sales<br/>Rahimafrooz Batteries Ltd<br/>Contact: +8801819466163", normal_style))
            
            doc.build(elements)
            buffer.seek(0)
            
            st.success("Professional PDF successfully toiri hoyeche!")
            st.download_button(
                label="📥 Download Professional PDF Offer",
                data=buffer,
                file_name=f"Price_Offer_{cust_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
