import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

st.set_page_config(page_title="Rahimafrooz Permanent Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Smart Price Offer Generator")
st.write("ডাটা সফলভাবে লোড হয়েছে। কাস্টমার ও ব্যাটারি সিলেক্ট করুন!")

@st.cache_data
def load_data():
    try:
        # Explicitly reading sheets with header at row index 1 (Excel row 2)
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
    # Clean column names
    df_cust.columns = df_cust.columns.astype(str).str.strip()
    df_price.columns = df_price.columns.astype(str).str.strip()
    
    # Clean up unnamed or empty columns if any
    df_cust = df_cust.loc[:, ~df_cust.columns.str.contains('^Unnamed')]
    df_price = df_price.loc[:, ~df_price.columns.str.contains('^Unnamed')]
    
    # Specific columns based on your Excel layout
    cust_col = 'Customer Name' if 'Customer Name' in df_cust.columns else df_cust.columns[0]
    brand_col = 'Brand' if 'Brand' in df_price.columns else df_price.columns[0]
    type_col = 'Type' if 'Type' in df_price.columns else df_price.columns[1]
    
    # Drop rows where essential names are missing
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
    
    if st.button("Generate Professional PDF Offer"):
        cust_matches = df_cust[df_cust[cust_col] == selected_customer]
        bat_matches = filtered_batteries[filtered_batteries[type_col] == selected_battery_type]
        
        if cust_matches.empty or bat_matches.empty:
            st.error("নির্বাচিত কাস্টমার বা ব্যাটারির তথ্য ডেটাবেজে পাওয়া যায়নি।")
        else:
            cust_row = cust_matches.iloc[0]
            bat_row = bat_matches.iloc[0]
                
            current_date = datetime.date.today().strftime("%d-%b-%Y")
            ref_no = f"RBL/CS/ACI/26-27/{datetime.date.today().strftime('%d%m%y')}"
                
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35)
            elements = []
            
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor("#B22222"),
                spaceAfter=4
            )
            
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14
            )

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
            
            sl_val = str(bat_row.get('SL', 1))
            type_val = str(bat_row.get('Type', ''))
            volt_val = str(bat_row.get('Volt', '12'))
            ah_val = str(bat_row.get('AH', ''))
            plate_val = str(bat_row.get('Plate', ''))
            retail_price = str(bat_row.get('Retail price with VAT', ''))
            special_price = str(bat_row.get('Special Offer With VAT', ''))
            vat_val = str(bat_row.get('VAT (15%)', ''))
            
            table_data = [
                ["SL", "Type", "Volt", "AH", "Plate", "Retail Price w/ VAT", "Special Offer w/ VAT", "VAT (15%)"],
                [sl_val, type_val, volt_val, ah_val, plate_val, retail_price, special_price, vat_val]
            ]
            
            t = Table(table_data, colWidths=[25, 110, 35, 35, 45, 95, 100, 85])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEAEA")),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8.5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#999999")),
            ]))
            
            elements.append(t)
            elements.append(Spacer(1, 15))
            
            elements.append(Paragraph("<b>Terms & Conditions:</b>", styles['Heading4']))
            terms_text = """
            • <b>Price Validity:</b> 15 Days.<br/>
            • <b>Warranty:</b> As per manufacturer standard terms from the date of delivery.<br/>
            • <b>Delivery Lead Time:</b> 15 days from the date of PO issuance.<br/>
            • <b>Delivery Place:</b> At your warehouse.<br/>
            • <b>Payment Terms:</b> 15 Days from the date of Bill submission.<br/>
            • <b>VAT/TAX:</b> Rahimafrooz will provide Mushok 6.3. AIT can be deducted as per current NBR rule.
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
