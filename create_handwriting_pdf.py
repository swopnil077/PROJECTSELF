from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register the handwriting font
pdfmetrics.registerFont(TTFont('PatrickHand', 'PatrickHand-Regular.ttf'))

def create_pdf(text, output_file):
    c = canvas.Canvas(output_file)
    c.setFont('PatrickHand', 14)
    
    # Split text into lines for better formatting
    lines = text.split('\n')
    
    y = 800  # Start from top of the page
    for line in lines:
        c.drawString(50, y, line)
        y -= 20  # Move down for next line
        
        # Add new page if needed
        if y < 50:
            c.showPage()
            c.setFont('PatrickHand', 14)
            y = 800
    
    c.save()
    print(f"New PDF saved as {output_file}")

if __name__ == "__main__":
    # Load the extracted text (replace this with your actual extracted text)
    with open("extracted_text.txt", "r", encoding="utf-8") as f:
        extracted_text = f.read()
    
    create_pdf(extracted_text, "output_handwriting.pdf")
