from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib import colors
from pptx import Presentation
from pptx.util import Inches, Pt
import os

TEXT_BLOCK_HEIGHT = Inches(0.8)
IMAGE_HEIGHT = Inches(2)
IMAGE_SPACING = Inches(0.2)
MAX_CONTENT_HEIGHT = Inches(7.0)
LOCAL_IMG_DIR = "assets\sample_images"

class DocumentGenerator():
    #@staticmethod
    def generate_pdf(doc_data, output_path: str):
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        for page in doc_data.pages:
            y = height - 50
            for element in page.text_items or []:
                if element.type == "title":
                    c.setFont("Helvetica-Bold", 20)
                    c.drawString(50, y, element.content)
                    y -= 30
                elif element.type == "subtitle":
                    c.setFont("Helvetica-BoldOblique", 16)
                    c.drawString(50, y, element.content)
                    y -= 25
                elif element.type == "paragraph":
                    c.setFont("Helvetica", 12)
                    lines = element.content.split('\n')
                    for line in lines:
                        c.drawString(50, y, line)
                        y -= 18
                else:
                    c.setFont("Helvetica", 12)
                    c.drawString(50, y, element.content)
                    y -= 20

            for image_name in page.images or []:
                image_path = os.path.join(LOCAL_IMG_DIR, image_name)
                if os.path.exists(image_path):
                    try:
                        c.drawImage(ImageReader(image_path), 50, y - 200, width=400, height=200, preserveAspectRatio=True)
                        y -= 220
                    except Exception as e:
                        print(f"❌ Error rendering image in PDF: {e}")

            c.showPage()

        c.save()

    #@staticmethod
    def generate_ppt(doc_data, output_path: str):
        prs = Presentation()

        for slide_data in doc_data.pages:
            slide = prs.slides.add_slide(prs.slide_layouts[5])

            # Customizing text dimensions
            num_blocks = len(slide_data.text_items or [])
            text_height_estimate = num_blocks * TEXT_BLOCK_HEIGHT
            textbox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8.5), text_height_estimate)
            tf = textbox.text_frame
            tf.word_wrap = True
            tf.auto_size = True

            for i, element in enumerate(slide_data.text_items or []):
                para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                para.text = element.content
                para.space_after = Pt(10)
                font = para.font

                if element.type == "title":
                    font.size = Pt(32)
                    font.bold = True
                elif element.type == "subtitle":
                    font.size = Pt(24)
                    font.italic = True
                elif element.type == "paragraph":
                    font.size = Pt(16)
                else:
                    font.size = Pt(14)

            # Customizing images
            image_top = Inches(0.5) + text_height_estimate + Inches(0.5)

            for img_name in slide_data.images or []:
                image_path = os.path.join(LOCAL_IMG_DIR, img_name)
                if os.path.exists(image_path):
                    # Check if this image fits on the current slide
                    if image_top + IMAGE_HEIGHT > MAX_CONTENT_HEIGHT:
                        # Create a new slide and reset
                        slide = prs.slides.add_slide(prs.slide_layouts[5])
                        image_top = Inches(0.5)

                    try:
                        slide.shapes.add_picture(image_path, Inches(0.5), image_top, height=IMAGE_HEIGHT)
                        image_top += IMAGE_HEIGHT + IMAGE_SPACING
                    except Exception as e:
                        print(f"❌ Error adding new image: {e}")

        prs.save(output_path)