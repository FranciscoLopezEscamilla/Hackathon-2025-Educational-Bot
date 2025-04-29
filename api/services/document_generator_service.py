import os
from fpdf import FPDF

class DocumentGenerator():
    @staticmethod
    def create(title: str, content: str) -> str:
        # ensure output dir
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "sample_file_from_agent.pdf")

        # initialize PDF
        pdf = FPDF()
        pdf.add_page()

        # register a Unicode‐capable TTF
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.multi_cell(0, 10, content)
        pdf.output(file_path)
        return file_path