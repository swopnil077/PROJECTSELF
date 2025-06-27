import streamlit as st
from PIL import Image, ImageDraw
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import pytesseract
from pytesseract import Output
import io
import os

# -------------------- Font Setup --------------------
font_folder = "fonts"
font_options = {
    "Patrick Hand": os.path.join(font_folder, "PatrickHand-Regular.ttf"),
    "Handlee": os.path.join(font_folder, "Handlee-Regular.ttf"),
    "Dancing Script": os.path.join(font_folder, "DancingScript-Regular.ttf"),
    "Homemade Apple": os.path.join(font_folder, "HomemadeApple-Regular.ttf"),
    "Indie Flower": os.path.join(font_folder, "IndieFlower-Regular.ttf"),
}

for name, path in font_options.items():
    simple_name = name.replace(" ", "")
    if os.path.isfile(path):
        try:
            pdfmetrics.registerFont(TTFont(simple_name, path))
        except Exception as e:
            st.error(f"Error loading font {name}: {e}")
    else:
        st.error(f"Font file not found: {path}")

# -------------------- Convert PDF to Images --------------------
@st.cache_data(show_spinner=False)
def pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes)

# -------------------- Generate PDF with New Font --------------------
def create_pdf_with_text_overlay(images, font_name):
    simple_font_name = font_name.replace(" ", "")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    pdf_width, pdf_height = letter

    for img in images:
        img_width, img_height = img.size
        ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')

        # Mask text only
        img_masked = img.convert("RGB").copy()
        draw = ImageDraw.Draw(img_masked)
        for i in range(len(ocr_data['text'])):
            if ocr_data['text'][i].strip():
                x, y, w, h = (
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i],
                )
                draw.rectangle([(x, y), (x + w, y + h)], fill="white")

        # Save modified image to buffer
        img_bytes = io.BytesIO()
        img_masked.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        c.drawImage(ImageReader(img_bytes), 0, 0, width=pdf_width, height=pdf_height)

        # Overlay new text at same positions
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i].strip()
            if text:
                x, y, w, h = (
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i],
                )
                pdf_x = (x / img_width) * pdf_width
                pdf_y = pdf_height - ((y + h) / img_height) * pdf_height
                font_size = max(8, (h / img_height) * pdf_height)
                c.setFont(simple_font_name, font_size)
                c.drawString(pdf_x, pdf_y, text)

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Handwriting Font Replacer", layout="centered")
st.title("📝 Handwriting Style Replacer")
st.markdown("This app replaces handwritten text with selected fonts while keeping diagrams and layout intact.")

uploaded_pdf = st.file_uploader("Upload your handwritten PDF", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    images = pdf_to_images(pdf_bytes)
    font_choice = st.selectbox("Choose a handwriting style", list(font_options.keys()))

    st.subheader("📄 Original Page Previews")
    for i, img in enumerate(images[:2]):
        st.image(img, caption=f"Original Page {i + 1}", use_container_width=True)

    st.subheader("✍️ Preview with Selected Font")
    preview_pdf = create_pdf_with_text_overlay(images[:2], font_choice)
    preview_imgs = convert_from_bytes(preview_pdf.getvalue())
    for i, img in enumerate(preview_imgs):
        st.image(img, caption=f"Preview Page {i + 1}", use_container_width=True)

    total_pages = len(images)
    cost_per_page = 10
    total_cost = total_pages * cost_per_page
    st.info(f"Total Pages: {total_pages} | Total Cost: Rs. {total_cost}")

    if st.button(f"Pay Rs. {total_cost} & Generate Full PDF"):
        result_pdf = create_pdf_with_text_overlay(images, font_choice)
        st.success("✅ PDF generated successfully!")
        st.download_button("Download PDF", result_pdf, file_name="converted_handwriting.pdf", mime="application/pdf")
