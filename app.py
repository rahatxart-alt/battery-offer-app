import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

st.set_page_config(page_title="Rahimafrooz Smart Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Smart Price Offer Generator")
st.write("কাস্টমার ও ব্যাটারি সিলেক্ট করুন। নিচের ফিল্ডগুলো থেকে যেকোনো মূল্য বা তথ্য পরিবর্তন করতে পারবেন!")

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
    st.error("Data.xlsx ফাইলটি রিড করা সম্ভব হয়নি।")
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
    
    st.write("### 📋 Selection Panel:")
    
    customer_list = sorted(df_cust[cust_col].unique().tolist())
    selected_customer = st.selectbox("Customer Name (Type to search):", options=customer_list)
    
    brand_list = sorted(df_price[brand_col].unique().tolist())
    selected_brand = st.selectbox("Select Battery Brand:", options=brand_list)
    
    filtered_batteries = df_price[df_price[brand_col] == selected_brand]
    battery_types = sorted(filtered_batteries[type_col].unique().tolist())
    
    selected_battery_type = st.selectbox("Battery Type (Type to search):", options=battery_types)
    
    # Fetch exact row for selected battery
    bat_row = filtered_batteries[filtered_batteries[type_col] == selected_battery_type].iloc[0]
    
    def clean_val(val, default=""):
        try:
            if pd.isna(val):
                return default
            return str(val).strip()
        except:
            return default

    def clean_num(val):
        try:
            return float(str(val).replace(',', '').strip())
        except:
            return 0.0

    # Extract default values from excel
    def_post = clean_val(bat_row.get('Post', 'I'), 'I')
    def_volt = clean_val(bat_row.get('Volt', '12'), '12')
    def_ah = clean_val(bat_row.get('AH', ''), '')
    def_plate = clean_val(bat_row.get('Plate', 'N/A'), 'N/A')
    def_btype = clean_val(bat_row.get('Type.1', bat_row.get('Type', 'SMF')), 'SMF')
    def_warranty = clean_val(bat_row.get('Warranty', '24M'), '24M')
    
    def_retail = clean_num(bat_row.get('Retail price with VAT', 0))
    def_offer_wo_vat = clean_num(bat_row.get('Offer Without VAT', 0))
    def_vat = clean_num(bat_row.get('VAT (15%)', 0))
    def_special = clean_num(bat_row.get('Special Offer With VAT', 0))
    if def_special == 0:
        def_special = def_retail

    st.write("---")
    st.write("### 🎛️ Vertical Price & Specifications Adjustment (ভার্টিকাল এডিটিং প্যানেল):")
    st.write("আপনার প্রয়োজনমতো নিচের ফিল্ডগুলোতে যেকোনো মান পরিবর্তন করতে পারবেন:")

    # Vertical Layout for all specifications and pricing
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        edit_post = st.text_input("Post", value=def_post)
        edit_volt = st.text_input("Volt", value=def_volt)
        edit_ah = st.text_input("AH", value=def_ah)
        edit_plate = st.text_input("Plate", value=def_plate)
        edit_btype = st.text_input("Type (SMF/LM)", value=def_btype)
        edit_warranty = st.text_input("Warranty", value=def_warranty)

    with col_v2:
        edit_retail = st.number_input("Retail Price w/ VAT (MRP)", value=def_retail, step=100.0)
        edit_offer_wo_vat = st.number_input("Offer Without VAT", value=def_offer_wo_vat, step=100.0)
        edit_vat = st.number_input("VAT (15%)", value=def_vat, step=10.0)
        edit_special = st.number_input("Special Offer With VAT (DP)", value=def_special, step=50.0)

    st.write("---")
    
    if st.button("Generate Professional PDF Offer"):
        cust_matches = df_cust[df_cust[cust_col] == selected_customer]
        
        if cust_matches.empty:
            st.error("নির্বাচিত কাস্টমার ডেটাবেজে পাওয়া যায়নি।")
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
            
            elements.append(Paragraph(f"<b>Price Offer of {selected_brand} Battery:</b>", styles['Heading4']))
            elements.append(Spacer(1, 5))
            
            # Using edited values in the PDF table
            table_data = [
                ["Brand", "Type", "Post", "Volt", "AH", "Plate", "Type", "Warranty", "Retail Price w/ VAT", "Offer Without VAT", "VAT (15%)", "Special Offer With VAT"],
                [
                    selected_brand, 
                    selected_battery_type, 
                    edit_post, 
                    edit_volt, 
                    edit_ah, 
                    edit_plate, 
                    edit_btype, 
                    edit_warranty, 
                    f"{edit_retail:,.2f}", 
                    f"{edit_offer_wo_vat:,.2f}" if edit_offer_wo_vat > 0 else "", 
                    f"{edit_vat:,.2f}" if edit_vat > 0 else "", 
                    f"{edit_special:,.2f}"
                ]
            ]
            
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
            
            st.success("প্রফেশনাল পিডিএফ সফলভাবে তৈরি হয়েছে!")
            st.download_button(
                label="📥 Download Professional PDF Offer",
                data=buffer,
                file_name=f"Price_Offer_{cust_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
