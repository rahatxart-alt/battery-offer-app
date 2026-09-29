import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Rahimafrooz Professional Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Advanced Price Offer Generator")
st.write("আপনার এক্সেল ফাইলটি আপলোড করুন (যেখানে Customer এবং Price শিট দুটোই সঠিকভাবে রয়েছে)।")

# Excel file upload field
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read Excel sheets with proper header row
        df_cust = pd.read_excel(uploaded_file, sheet_name='Customer', header=0)
        df_price = pd.read_excel(uploaded_file, sheet_name='Price', header=0)
    except Exception as e:
        st.error(f"এক্সেল ফাইল পড়তে সমস্যা হয়েছে: {e}")
        st.stop()
        
    st.success("এক্সেল ফাইল সফলভাবে এবং সঠিকভাবে লোড হয়েছে!")
    
    # Clean column names
    df_cust.columns = df_cust.columns.str.strip()
    df_price.columns = df_price.columns.str.strip()
    
    # Drop rows where essential columns are NaN
    df_cust = df_cust.dropna(subset=['Customer Name'])
    df_price = df_price.dropna(subset=['Brand', 'Type'])
    
    # Selection interface
    st.write("### 📋 কাস্টমার ও ব্যাটারি তথ্য নির্বাচন করুন:")
    
    customer_list = df_cust['Customer Name'].tolist()
    selected_customer = st.selectbox("কাস্টমার সিলেক্ট করুন:", customer_list)
    
    brand_list = df_price['Brand'].unique().tolist()
    selected_brand = st.selectbox("ব্যাটারি ব্র্যান্ড সিলেক্ট করুন:", brand_list)
    
    filtered_batteries = df_price[df_price['Brand'] == selected_brand]
    selected_battery_type = st.selectbox("ব্যাটারি টাইপ সিলেক্ট করুন:", filtered_batteries['Type'].tolist())
    
    if st.button("Generate Professional PDF Offer"):
        # Fetch specific rows
        cust_row = df_cust[df_cust['Customer Name'] == selected_customer].iloc[0]
        bat_row = filtered_batteries[filtered_batteries['Type'] == selected_battery_type].iloc[0]
            
        # PDF generation buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35)
        elements = []
        
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        styles = getSampleStyleSheet()
        
        # Custom styles
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

        # Header Info
        elements.append(Paragraph("<b>RAHIMAFROOZ BATTERIES LIMITED</b>", title_style))
        elements.append(Paragraph("Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215 | Tel: 02-9113696", normal_style))
        elements.append(Spacer(1, 10))
        
        # Reference and Date
        elements.append(Paragraph("<b>Ref:</b> RBL/CS/ACI/26-27/290926", normal_style))
        elements.append(Paragraph("<b>Date:</b> 29-Sep-2026", normal_style))
        elements.append(Spacer(1, 10))
        
        # Customer Details Block
        cust_name = str(cust_row.get('Customer Name', ''))
        concern_person = str(cust_row.get('Concern Person', ''))
        contact_no = str(cust_row.get('Contact Number', ''))
        cust_address = str(cust_row.get('Company Address', ''))
        
        to_address = f"<b>To:</b><br/><b>{cust_name}</b><br/><b>Attn:</b> {concern_person} (Mob: {contact_no})<br/>{cust_address}"
        elements.append(Paragraph(to_address, normal_style))
        elements.append(Spacer(1, 12))
        
        # Subject & Greeting
        elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
        elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", normal_style))
        elements.append(Spacer(1, 12))
        
        # Table Section Header
        elements.append(Paragraph(f"<b>Price Offer of {selected_brand} Battery:</b>", styles['Heading4']))
        elements.append(Spacer(1, 5))
        
        # Extract exact values from Excel
        sl_val = str(bat_row.get('SL', 1))
        type_val = str(bat_row.get('Type', ''))
        volt_val = str(bat_row.get('Volt', '12'))
        ah_val = str(bat_row.get('AH', ''))
        plate_val = str(bat_row.get('Plate', ''))
        retail_price = str(bat_row.get('Retail price with VAT', ''))
        special_price = str(bat_row.get('Special Offer With VAT', ''))
        vat_val = str(bat_row.get('VAT (15%)', ''))
        
        # Professional Table Data mapping
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
        
        # Terms & Conditions Block
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
        
        # Signature block
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
