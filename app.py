import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Battery Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Battery Price Offer Generator")
st.write("আপনার এক্সেল ফাইলটি আপলোড করুন (যেখানে Customer এবং Price দুটো শিটই রয়েছে)।")

# Excel file upload field
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Read both sheets from Excel file
    try:
        df_cust = pd.read_excel(uploaded_file, sheet_name='Customer')
    except:
        df_cust = pd.read_excel(uploaded_file, sheet_name=0)  # Fallback to first sheet
        
    try:
        df_price = pd.read_excel(uploaded_file, sheet_name='Price')
    except:
        df_price = pd.read_excel(uploaded_file, sheet_name=1)  # Fallback to second sheet
        
    st.success("এক্সেল ফাইল সফলভাবে আপলোড হয়েছে!")
    
    # Selection options in web interface
    st.write("### কাস্টমার ও ব্যাটারি সিলেক্ট করুন:")
    customer_list = df_cust['Customer Name'].unique().tolist()
    selected_customer = st.selectbox("কাস্টমার সিলেক্ট করুন:", customer_list)
    
    brand_list = df_price['Brand'].unique().tolist()
    selected_brand = st.selectbox("ব্র্যান্ড সিলেক্ট করুন:", brand_list)
    
    # Filter batteries based on selected brand
    filtered_batteries = df_price[df_price['Brand'] == selected_brand]
    selected_battery_type = st.selectbox("ব্যাটারি টাইপ সিলেক্ট করুন:", filtered_batteries['Type'].tolist())
    
    if st.button("Generate PDF Offer"):
        # Get customer row data
        cust_row = df_cust[df_cust['Customer Name'] == selected_customer].iloc[0]
        
        # Get battery row data
        bat_row = filtered_batteries[filtered_batteries['Type'] == selected_battery_type].iloc[0]
            
        # PDF generation memory buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        styles = getSampleStyleSheet()
        
        # Header Info
        elements.append(Paragraph("<b>RAHIMAFROOZ BATTERIES LIMITED</b>", styles['Heading1']))
        elements.append(Paragraph("Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Customer & Concern Details
        cust_name = cust_row.get('Customer Name', '')
        concern_person = cust_row.get('Concern Person', '')
        contact_no = cust_row.get('Contact Number', '')
        cust_address = cust_row.get('Company Address', '')
        
        elements.append(Paragraph("<b>Ref:</b> RBL/CS/ACI/26-27/290926", styles['Normal']))
        elements.append(Paragraph("<b>Date:</b> 29-Sep-2026", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        to_address = f"<b>To:</b><br/>{cust_name}<br/><b>Attn:</b> {concern_person} (Mob: {contact_no})<br/>{cust_address}"
        elements.append(Paragraph(to_address, styles['Normal']))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
        elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Dynamic Table Data Section from Price Sheet
        elements.append(Paragraph(f"<b>Price Offer of {selected_brand} Battery:</b>", styles['Heading4']))
        
        table_data = [
            ["SL", "Type", "Volt", "AH", "Plate", "Retail price with VAT", "Special Offer With VAT", "VAT (15%)"],
            [
                str(bat_row.get('SL', 1)),
                str(bat_row.get('Type', '')),
                str(bat_row.get('Volt', '')),
                str(bat_row.get('AH', '')),
                str(bat_row.get('Plate', '')),
                str(bat_row.get('Retail price with VAT', '')),
                str(bat_row.get('Special Offer With VAT', '')),
                str(bat_row.get('VAT (15%)', ''))
            ]
        ]
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 15))
        
        # Terms and conditions
        elements.append(Paragraph("<b>Terms & Conditions:</b>", styles['Heading4']))
        terms_text = """
        • Price Validity: 15 Days.<br/>
        • Warranty: As per manufacturer standard terms.<br/>
        • Delivery Place: At your warehouse.<br/>
        • Payment Terms: 15 Days from the date of Bill submission.
        """
        elements.append(Paragraph(terms_text, styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        
        st.success("পিডিএফ সফলভাবে তৈরি হয়েছে!")
        st.download_button(
            label="📥 Download PDF Offer",
            data=buffer,
            file_name=f"Price_Offer_{cust_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
