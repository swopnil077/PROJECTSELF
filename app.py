import streamlit as st
from PIL import Image, ImageOps, ImageFilter
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
import pytesseract
import io
import os

# ------------------- Font Options -------------------
# Assuming you have a 'fonts' folder with these files inside your project directory
font_folder = "fonts"
font_options = {
    "Patrick Hand": os.path.join(font_folder, "PatrickHand-Regular.ttf"),
    "Handlee": os.path.join(font_folder, "Handlee-Regular.ttf"),
    "Dancing Script": os.path.join(font_folder, "DancingScript-Regular.ttf"),
    "Homemade Apple": os.path.join(font_folder, "HomemadeApple-Regular.ttf"),
    "Indie Flower": os.path.join(font_folder, "IndieFlower-Regular.ttf"),
}

# Register fonts once at startup with simplified font names (no spaces)
for font_name, font_path in font_options.items():
    simple_name = font_name.replace(" ", "")
    if os.path.isfile(font_path):
        try:
            pdfmetrics.registerFont(TTFont(simple_name, font_path))
        except Exception as e:
            st.error(f"Error loading font file {font_path}: {e}")
    else:
        st.error(f"Font file not found: {font_path}. Please add it to the 'fonts' folder.")

# ------------------- Cached Functions -------------------

@st.cache_data(show_spinner=False)
def pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes)

@st.cache_data(show_spinner=False)
def generate_sample_pages(_images, font_name, num_pages=2):
    previews = []
    simple_font_name = font_name.replace(" ", "")

    for i in range(min(num_pages, len(_images))):
        img = _images[i].convert("L")
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, lang='eng')

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont(simple_font_name, 14)

        y = 750
        for line in text.split('\n'):
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                break
        c.save()

        buffer.seek(0)
        preview_img = convert_from_bytes(buffer.getvalue())[0]
        img_byte_arr = io.BytesIO()
        preview_img.save(img_byte_arr, format='PNG')
        previews.append(img_byte_arr.getvalue())

    return previews

def generate_handwriting_pdf(images, font_name):
    simple_font_name = font_name.replace(" ", "")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont(simple_font_name, 14)

    for page in images:
        img = page.convert("L")
        img = ImageOps.autocontrast(img)
        img = img.filter(ImageFilter.SHARPEN)
        text = pytesseract.image_to_string(img, lang='eng')

        y = 750
        for line in text.split('\n'):
            c.drawString(50, y, line)
            y -= 20
            if y < 50:
                c.showPage()
                c.setFont(simple_font_name, 14)
                y = 750
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

def get_esewa_payment_url(amount, pid="123456789", scd="EPAYTEST"):
    return_url = "http://localhost:8501?payment=success"
    fail_url = "http://localhost:8501?payment=failed"

    url = f"https://uat.esewa.com.np/epay/main?"
    url += f"amt={amount}&pdc=0&psc=0&txAmt=0&"
    url += f"tAmt={amount}&pid={pid}&scd={scd}&"
    url += f"su={return_url}&fu={fail_url}"
    return url

# ------------------- Streamlit UI -------------------

st.title("📝 Handwriting Converter Web App")

uploaded_pdf = st.file_uploader("Upload your handwritten PDF", type="pdf")

if uploaded_pdf is not None:
    pdf_bytes = uploaded_pdf.read()
    st.session_state['pdf_bytes'] = pdf_bytes

if 'pdf_bytes' in st.session_state:
    images = pdf_to_images(st.session_state['pdf_bytes'])

    selected_font_name = st.selectbox(
        "✍️ Choose handwriting style",
        list(font_options.keys()),
        key="font_select"
    )

    # Generate sample previews passing font name (string, hashable)
    sample_previews = generate_sample_pages(images, selected_font_name, num_pages=2)

    st.markdown("### 📄 Sample Preview (First 2 Pages)")
    for i, img_data in enumerate(sample_previews):
        st.image(img_data, caption=f"Preview Page {i + 1}", use_container_width=True)

    total_pages = len(images)
    total_cost = total_pages * 10  # Rs. 10 per page price example
    st.info(f"💰 Total cost: Rs. {total_cost}")

    # Check payment status from query params
    query_params = st.query_params
    payment_status = query_params.get("payment", [None])[0]

    if payment_status == "success":
        st.success("✅ Payment successful! Generating your final PDF...")
        final_pdf = generate_handwriting_pdf(images, selected_font_name)
        st.download_button(
            label="📥 Download Final PDF",
            data=final_pdf,
            file_name="converted_handwriting.pdf",
            mime="application/pdf"
        )
    elif payment_status == "failed":
        st.error("❌ Payment failed. Please try again.")
    else:
        st.markdown("### 💳 Proceed to Payment")
        payment_url = get_esewa_payment_url(total_cost)
        st.markdown(f"[Click here to pay via eSewa]({payment_url})", unsafe_allow_html=True)
        st.warning("⚠️ After payment, you will be redirected here to download your file.")
