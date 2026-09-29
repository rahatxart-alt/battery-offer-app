import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io
import datetime

st.set_page_config(page_title="Rahimafrooz Smart Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Smart Price Offer Generator")
st.write("ডাটা সফলভাবে লোড হয়েছে। কাস্টমার ও ব্যাটারি সিলেক্ট করুন এবং প্রয়োজনমতো মূল্য পরিবর্তন করুন!")

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
    
    st.write("### 📋 Selection & Price Customization Panel:")
    
    customer_list = sorted(df_cust[cust_col].unique().tolist())
    selected_customer = st.selectbox("Customer Name (Type to search):", options=customer_list)
    
    brand_list = sorted(df_price[brand_col].unique().tolist())
    selected_brand = st.selectbox("Select Battery Brand:", options=brand_list)
    
    filtered_batteries = df_price[df_price[brand_col] == selected_brand]
    battery_types = sorted(filtered_batteries[type_col].unique().tolist())
    
    selected_battery_type = st.selectbox("Battery Type (Type to search):", options=battery_types)
    
    # Fetch default values from Excel for the selected battery
    bat_row = filtered_batteries[filtered_batteries[type_col] == selected_battery_type].iloc[0]
    
    default_special_price = bat_row.get('Special Offer With VAT', 0)
    try:
        default_special_price = float(default_special_price)
    except:
        default_special_price = 0.0

    st.write("---")
    st.write("### 💰 Price Adjustment:")
    custom_special_price = st.number_input(
        "Special Offer With VAT (ইচ্ছেমতো কমিয়ে বসাতে পারেন):", 
        value=default_special_price, 
        step=100.0
    )
    
    if st.button("Generate Professional PDF Offer"):
        cust_matches = df_cust[df_cust[cust_col] == selected_customer]
        
        if cust_matches.empty:
            st.error("নির্বাচিত কাস্টমার ডেটাবেজে পাওয়া যায়নি।")
        else:
            cust_row = cust_matches.iloc[0]
                
            current_date = datetime.date.today().strftime("%d-%b-%Y")
            ref_no = f"RBL/CS/ACI/26-27/{datetime.date.today().strftime('%d%m%y')}"
                
            buffer = io.BytesIO()
            # Landscape orientation to accommodate all columns nicely
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
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
            
            # Extracting all columns matching your excel structure
            brand_val = str(bat_row.get('Brand', selected_brand))
            type_val = str(bat_row.get('Type', selected_battery_type))
            post_val = str(bat_row.get('Post', 'I'))
            volt_val = str(bat_row.get('Volt', '12'))
            ah_val = str(bat_row.get('AH', ''))
            plate_val = str(bat_row.get('Plate', 'N/A'))
            bat_type_col = str(bat_row.get('Type.1', bat_row.get('Type', 'SMF'))) # Handling duplicate 'Type' column if present
            warranty_val = str(bat_row.get('Warranty', '24M'))
            retail_price = str(bat_row.get('Retail price with VAT', ''))
            offer_wo_vat = str(bat_row.get('Offer Without VAT', ''))
            vat_val = str(bat_row.get('VAT (15%)', ''))
            
            formatted_special_price = f"{custom_special_price:,.2f}"
            
            table_data = [
                ["Brand", "Type", "Post", "Volt", "AH", "Plate", "Type", "Warranty", "Retail Price w/ VAT", "Offer Without VAT", "VAT (15%)", "Special Offer With VAT"],
                [brand_val, type_val, post_val, volt_val, ah_val, plate_val, bat_type_col, warranty_val, str(retail_price), str(offer_wo_vat), str(vat_val), formatted_special_price]
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
