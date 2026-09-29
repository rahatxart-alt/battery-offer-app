import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Battery Price Offer Generator", layout="centered")

st.title("🔋 Rahimafrooz Battery Price Offer Generator")
st.write("Apnar Excel file upload korun jekhane customer name, address, ebong battery er info/price gulo ache.")

# Excel file upload field
uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Excel pore neoa
    df = pd.read_excel(uploaded_file)
    st.success("Excel file successfully upload hoyeche!")
    
    st.write("### Data Preview:")
    st.dataframe(df.head())
    
    # Customer select ba row select korar option
    customer_list = df['Customer_Name'].unique() if 'Customer_Name' in df.columns else df.iloc[:, 0].tolist()
    selected_customer = st.selectbox("Customer Select korun:", customer_list)
    
    if st.button("Generate PDF Offer"):
        # Select kora customer er data filter kora
        if 'Customer_Name' in df.columns:
            row = df[df['Customer_Name'] == selected_customer].iloc[0]
        else:
            row = df.iloc[0]
            
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
        
        # Customer Details
        cust_name = row.get('Customer_Name', 'Valued Customer')
        cust_address = row.get('Customer_Address', 'Dhaka, Bangladesh')
        ref_no = row.get('Ref_No', 'RBL/CS/ACI/26-27/290926')
        date_str = row.get('Date', '29-Sep-2026')
        
        elements.append(Paragraph(f"<b>Ref:</b> {ref_no}", styles['Normal']))
        elements.append(Paragraph(f"<b>Date:</b> {date_str}", styles['Normal']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>To:</b><br/>{cust_name}<br/>{cust_address}", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("<b>Subject: Price offer for supplying Rahimafrooz battery.</b>", styles['Heading3']))
        elements.append(Paragraph("Dear Sir, Greetings!<br/>In reference to your mail, please find price offer & warranty terms for Rahimafrooz battery to serve your requirement.", styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Table Data from Excel
        elements.append(Paragraph("<b>Low Maintenance Battery:</b>", styles['Heading4']))
        
        # Dynamic values from excel or default fallback
        table_data = [
            ["SL", "Type", "Volt", "Plate", "AH", "Retail price with VAT", "Special Offered price with VAT", "VAT (15%)", "Total Offered price with VAT"],
            [
                str(row.get('SL', 1)),
                str(row.get('Type', 'PCM27')),
                str(row.get('Volt', '12')),
                str(row.get('Plate', '27')),
                str(row.get('AH', '160')),
                str(row.get('Retail_Price', '27,120.00')),
                str(row.get('Special_Price', '17,826.09')),
                str(row.get('VAT', '2,673.91')),
                str(row.get('Total_Price', '20,500'))
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
        
        # Terms and conditions summary
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
        
        st.success("PDF successfully toiri hoyeche!")
        st.download_button(
            label="📥 Download PDF Offer",
            data=buffer,
            file_name=f"Price_Offer_{cust_name}.pdf",
            mime="application/pdf"
        )