import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageFilter, ImageOps
import os
import io

# Set up Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Register handwriting font
font_path = "PatrickHand-Regular.ttf"
pdfmetrics.registerFont(TTFont("PatrickHand", font_path))

# Title
st.title("📝 Handwriting Style Changer")

uploaded_pdf = st.file_uploader("Upload handwritten PDF", type=["pdf"])

if uploaded_pdf:
    st.success("✅ PDF uploaded!")
    
    # Convert PDF to images
    images = convert_from_bytes(uploaded_pdf.read())
    total_pages = len(images)
    st.info(f"📄 Total pages: {total_pages}")
    
    rate = 10
    total_cost = total_pages * rate
    st.info(f"💰 ₹{rate} per page × {total_pages} pages = ₹{total_cost}")
    
    if st.button("💸 Simulate Payment & Generate PDF"):
        all_text = ""
        
        # Process each page
        for i, img in enumerate(images):
            # Enhance image
            img = img.convert("L")
            img = ImageOps.autocontrast(img)
            img = img.filter(ImageFilter.SHARPEN)
            
            # OCR
            text = pytesseract.image_to_string(img, lang='eng')
            all_text += text + "\n\n"
        
        # Generate PDF in memory
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("PatrickHand", 14)
        
        lines = all_text.split("\n")
        y = 800
        for line in lines:
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                c.setFont("PatrickHand", 14)
                y = 800
        c.save()
        
        # Show download button
        st.success("✅ Handwriting-style PDF created!")
        st.download_button(
            label="📥 Download Output PDF",
            data=buffer.getvalue(),
            file_name="handwriting_output.pdf",
            mime="application/pdf"
        )
