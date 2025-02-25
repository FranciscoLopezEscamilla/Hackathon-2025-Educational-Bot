import os
from fpdf import FPDF

class DocumentGenerator():
    @staticmethod
    def create(title: str, content: str) -> str:
        # create directory if tit does not exist
        output_dir: str = "output"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "Sample_PDF_document.pdf")

        # create the PDF file
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font(family="Arial", size=12)
        pdf.cell(200, 10, title, ln=True, align="C")
        pdf.multi_cell(0, 10, content)
        pdf.output(file_path)

        return file_path