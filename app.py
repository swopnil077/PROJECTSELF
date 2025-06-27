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
from collections import defaultdict

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

# -------------------- Generate PDF with Word-Level Layout and Adjustable Spacing + Alignment + Font Size --------------------
def create_pdf_with_aligned_text(images, font_name, word_spacing, text_alignment_offset, vertical_alignment_offset, font_size_scale):
    simple_font_name = font_name.replace(" ", "")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    pdf_width, pdf_height = letter

    for img in images:
        img_width, img_height = img.size
        scale_x = pdf_width / img_width
        scale_y = pdf_height / img_height

        ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')

        # Mask original text from image
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

        # Use masked image as background
        img_bytes = io.BytesIO()
        img_masked.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        c.drawImage(ImageReader(img_bytes), 0, 0, width=pdf_width, height=pdf_height)

        # Group words by line
        lines = defaultdict(list)
        for i in range(len(ocr_data['text'])):
            if ocr_data['text'][i].strip():
                key = (ocr_data['block_num'][i], ocr_data['par_num'][i], ocr_data['line_num'][i])
                lines[key].append({
                    'text': ocr_data['text'][i].strip(),
                    'x': ocr_data['left'][i],
                    'y': ocr_data['top'][i],
                    'w': ocr_data['width'][i],
                    'h': ocr_data['height'][i],
                })

        # Draw words with adjustable spacing, horizontal & vertical offset, and font size scale
        for line_words in lines.values():
            if not line_words:
                continue
            # Sort words left to right
            line_words = sorted(line_words, key=lambda w: w['x'])
            # Calculate Y position from first word in line with vertical offset
            first_word = line_words[0]
            y = pdf_height - ((first_word['y'] + first_word['h']) * scale_y) + vertical_alignment_offset
            # Use average height for font size scaled by user input
            avg_h = sum(w['h'] for w in line_words) / len(line_words)
            font_size = max(6, avg_h * scale_y * 0.9 * font_size_scale)
            c.setFont(simple_name, font_size)

            # Start at first word's scaled x plus horizontal offset
            x_cursor = line_words[0]['x'] * scale_x + text_alignment_offset

            for word in line_words:
                text = word['text']
                c.drawString(x_cursor, y, text)
                word_width = c.stringWidth(text, simple_name, font_size)
                x_cursor += word_width + word_spacing

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Handwriting Font Replacer", layout="centered")
st.title("📝 Handwriting Style Replacer")
st.markdown("Replace handwritten text with clean fonts while keeping diagrams, tables, and layout intact.")

uploaded_pdf = st.file_uploader("Upload your handwritten PDF", type=["pdf"])
if uploaded_pdf:
    pdf_bytes = uploaded_pdf.read()
    images = pdf_to_images(pdf_bytes)
    font_choice = st.selectbox("Choose a handwriting style", list(font_options.keys()))

    st.subheader("📄 Original Page Previews")
    for i, img in enumerate(images[:2]):
        st.image(img, caption=f"Original Page {i + 1}", use_container_width=True)

    st.subheader("✍️ Preview with Selected Font")

    # Default values for sliders
    default_word_spacing = 0
    default_text_offset = 0
    default_vertical_offset = 0
    default_font_size_scale = 1.0

    preview_pdf = create_pdf_with_aligned_text(
        images[:2],
        font_choice,
        default_word_spacing,
        default_text_offset,
        default_vertical_offset,
        default_font_size_scale,
    )
    preview_imgs = convert_from_bytes(preview_pdf.getvalue())
    for i, img in enumerate(preview_imgs):
        st.image(img, caption=f"Preview Page {i + 1}", use_container_width=True)

    # Sliders below preview
    col1, col2 = st.columns(2)
    with col1:
        word_spacing = st.slider("Adjust word spacing (pixels)", -10, 30, default_word_spacing, 1)
        vertical_alignment_offset = st.slider("Adjust vertical alignment (pixels)", -30, 30, default_vertical_offset, 1)
    with col2:
        text_alignment_offset = st.slider("Adjust horizontal alignment (pixels)", -30, 30, default_text_offset, 1)
        font_size_scale = st.slider("Adjust font size multiplier", 0.5, 2.0, default_font_size_scale, 0.05)

    # Update preview when sliders or font change
    preview_pdf = create_pdf_with_aligned_text(
        images[:2],
        font_choice,
        word_spacing,
        text_alignment_offset,
        vertical_alignment_offset,
        font_size_scale,
    )
    preview_imgs = convert_from_bytes(preview_pdf.getvalue())
    for i, img in enumerate(preview_imgs):
        st.image(img, caption=f"Preview Page {i + 1}", use_container_width=True)

    total_pages = len(images)
    cost_per_page = 10
    total_cost = total_pages * cost_per_page
    st.info(f"Total Pages: {total_pages} | Total Cost: Rs. {total_cost}")

    if st.button(f"Pay Rs. {total_cost} & Generate Full PDF"):
        result_pdf = create_pdf_with_aligned_text(
            images,
            font_choice,
            word_spacing,
            text_alignment_offset,
            vertical_alignment_offset,
            font_size_scale,
        )
        st.success("✅ PDF generated successfully!")
        st.download_button(
            "Download PDF",
            result_pdf,
            file_name="converted_handwriting.pdf",
            mime="application/pdf",
        )
