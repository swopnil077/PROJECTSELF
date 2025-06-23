import pytesseract
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageFilter, ImageOps
import os
import sys

# Setup
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pdf_file = "input.pdf"
handwriting_font = "PatrickHand-Regular.ttf"
rate_per_page = 10

# Check font file
if not os.path.exists(handwriting_font):
    print(f"❌ Missing handwriting font file: {handwriting_font}")
    sys.exit()

# Convert PDF to images
pages = convert_from_path(pdf_file)
total_pages = len(pages)
print(f"\n📄 Total pages in PDF: {total_pages}")
total_cost = total_pages * rate_per_page
print(f"💰 Price per page: ₹{rate_per_page}")
print(f"🧾 Total cost: ₹{total_cost}")

# Simulate payment
confirm = input("\n💸 Type 'yes' to proceed with payment: ").strip().lower()
if confirm != "yes":
    print("❌ Payment not confirmed. Exiting.")
    sys.exit()
else:
    print("✅ Payment confirmed! Generating handwriting PDF...")

# Extract and clean text
os.makedirs("images", exist_ok=True)
all_text = ""

for i, page in enumerate(pages):
    image_path = f"images/page_{i + 1}.png"
    page.save(image_path, "PNG")

    # Enhance image for better OCR
    img = Image.open(image_path).convert("L")
    img = ImageOps.autocontrast(img)
    img = img.filter(ImageFilter.SHARPEN)
    img.save("cleaned.png")

    text = pytesseract.image_to_string("cleaned.png", lang='eng')
    all_text += text + "\n\n"

# Save text
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

# Register font and create output PDF
pdfmetrics.registerFont(TTFont("PatrickHand", handwriting_font))
c = canvas.Canvas("output_handwriting.pdf")
c.setFont("PatrickHand", 14)

lines = all_text.split('\n')
y = 800

for line in lines:
    c.drawString(50, y, line)
    y -= 20
    if y < 50:
        c.showPage()
        c.setFont("PatrickHand", 14)
        y = 800

c.save()
print("\n📦 output_handwriting.pdf generated successfully.")
