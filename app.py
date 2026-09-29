import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Battery Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Battery Price Offer Generator")
st.write("আপনার এক্সেল ফাইলটি আপলোড করুন (যেখানে কাস্টমার নেম, অ্যাড্রেস এবং ব্যাটারির তথ্য রয়েছে)।")

# Excel file upload field
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Excel file পড়া
    df = pd.read_excel(uploaded_file, sheet_name='address')  # আপনার 'address' শিট থেকে ডাটা নেবে
    st.success("এক্সেল ফাইল সফলভাবে আপলোড হয়েছে!")
    
    st.write("### ডাটা প্রিভিউ:")
    st.dataframe(df.head())
    
    # Customer Name সিলেক্ট করার অপশন
    customer_list = df['Customer Name'].unique().tolist()
    selected_customer = st.selectbox("কাস্টমার সিলেক্ট করুন:", customer_list)
    
    if st.button("Generate PDF Offer"):
        # সিলেক্ট করা কাস্টমার অনুযায়ী রো ফিল্টার করা
        row = df[df['Customer Name'] == selected_customer].iloc[0]
            
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
        cust_name = row.get('Customer Name', '')
        concern_person = row.get('Concern Person', '')
        contact_no = row.get('Contact Number', '')
        cust_address = row.get('Company Address', '')
        
        elements.append(Paragraph("<b>Ref:</b> RBL/CS/ACI/26-27/290926", styles['Normal']))
        elements.append(Paragraph("<b>Date:</b> 29-Sep-2026", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        to_address = f"<b>To:</b><br/>{cust_name}<br/><b>Attn:</b> {concern_person} (Mob: {contact_no})<br/>{cust_address}"
        elements.append(Paragraph(to_address, styles['Normal']))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
        elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Table Data Section
        elements.append(Paragraph("<b>Low Maintenance Battery:</b>", styles['Heading4']))
        
        table_data = [
            ["SL", "Type", "Volt", "Plate", "AH", "Retail price with VAT", "Special Offered price with VAT", "VAT (15%)", "Total Offered price with VAT"],
            ["1", "PCM27", "12", "27", "160", "27,120.00", "17,826.09", "2,673.91", "20,500"]
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
        • Warranty: 15 months warranty from the date of delivery.<br/>
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
