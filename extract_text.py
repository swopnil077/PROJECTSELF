import pytesseract
from pdf2image import convert_from_path
import os

# Setup
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pdf_file = "input.pdf"
rate_per_page = 10  # You can change this price

# Convert PDF pages to images
pages = convert_from_path(pdf_file)
total_pages = len(pages)
print(f"\n📄 Total pages in PDF: {total_pages}")

# Create output folder for images
os.makedirs("images", exist_ok=True)

# Extract text and save images
all_text = ""

for i, page in enumerate(pages):
    image_path = f"images/page_{i + 1}.png"
    page.save(image_path, "PNG")

    text = pytesseract.image_to_string(image_path, lang='eng')
    print(f"\n📝 Text from page {i + 1}:\n{'-'*40}\n{text}")

    all_text += text + "\n\n"

# Save extracted text
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

# Calculate price
total_cost = total_pages * rate_per_page
print(f"\n💰 Price per page: ₹{rate_per_page}")
print(f"🧾 Total cost: ₹{total_cost}")

# Optional: Simulate payment step
print("\n➡️ Please proceed to payment before downloading the new PDF (simulated for now).")
