import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Battery Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Battery Price Offer Generator")
st.write("আপনার এক্সেল ফাইলটি আপলোড করুন (যেখানে Customer এবং Price শিট দুটোই রয়েছে)।")

# Excel file upload field
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_cust = pd.read_excel(uploaded_file, sheet_name='Customer')
    except:
        df_cust = pd.read_excel(uploaded_file, sheet_name=0)
        
    try:
        df_price = pd.read_excel(uploaded_file, sheet_name='Price')
    except:
        df_price = pd.read_excel(uploaded_file, sheet_name=1)
        
    st.success("এক্সেল ফাইল সফলভাবে আপলোড হয়েছে!")
    
    # Clean column names (strip extra spaces if any)
    df_cust.columns = df_cust.columns.str.strip()
    df_price.columns = df_price.columns.str.strip()
    
    # Identify proper column names safely
    cust_col = 'Customer Name' if 'Customer Name' in df_cust.columns else df_cust.columns[1]
    brand_col = 'Brand' if 'Brand' in df_price.columns else df_price.columns[1]
    type_col = 'Type' if 'Type' in df_price.columns else df_price.columns[3]
    
    st.write("### কাস্টমার ও ব্যাটারি সিলেক্ট করুন:")
    customer_list = df_cust[cust_col].dropna().unique().tolist()
    selected_customer = st.selectbox("কাস্টমার সিলেক্ট করুন:", customer_list)
    
    brand_list = df_price[brand_col].dropna().unique().tolist()
    selected_brand = st.selectbox("ব্র্যান্ড সিলেক্ট করুন:", brand_list)
    
    filtered_batteries = df_price[df_price[brand_col] == selected_brand]
    selected_battery_type = st.selectbox("ব্যাটারি টাইপ সিলেক্ট করুন:", filtered_batteries[type_col].dropna().astype(str).tolist())
    
    if st.button("Generate PDF Offer"):
        cust_row = df_cust[df_cust[cust_col] == selected_customer].iloc[0]
        bat_row = filtered_batteries[filtered_batteries[type_col].astype(str) == selected_battery_type].iloc[0]
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph("<b>RAHIMAFROOZ BATTERIES LIMITED</b>", styles['Heading1']))
        elements.append(Paragraph("Business Office: 705 Nakhalpara, Tejgaon, Dhaka 1215", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        cust_name = str(cust_row.get(cust_col, ''))
        concern_person = str(cust_row.get('Concern Person', ''))
        contact_no = str(cust_row.get('Contact Number', ''))
        cust_address = str(cust_row.get('Company Address', ''))
        
        elements.append(Paragraph("<b>Ref:</b> RBL/CS/ACI/26-27/290926", styles['Normal']))
        elements.append(Paragraph("<b>Date:</b> 29-Sep-2026", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        to_address = f"<b>To:</b><br/>{cust_name}<br/><b>Attn:</b> {concern_person} (Mob: {contact_no})<br/>{cust_address}"
        elements.append(Paragraph(to_address, styles['Normal']))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
        elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(f"<b>Price Offer of {selected_brand} Battery:</b>", styles['Heading4']))
        
        # Dynamic extraction from Price sheet columns
        volt_val = bat_row.get('Volt', '12')
        ah_val = bat_row.get('AH', '')
        plate_val = bat_row.get('Plate', '')
        retail_price = bat_row.get('Retail price with VAT', '')
        special_price = bat_row.get('Special Offer With VAT', '')
        vat_val = bat_row.get('VAT (15%)', '')
        
        table_data = [
            ["SL", "Type", "Volt", "AH", "Plate", "Retail price with VAT", "Special Offer With VAT", "VAT (15%)"],
            [
                str(bat_row.get('SL', 1)),
                str(selected_battery_type),
                str(volt_val),
                str(ah_val),
                str(plate_val),
                str(retail_price),
                str(special_price),
                str(vat_val)
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
