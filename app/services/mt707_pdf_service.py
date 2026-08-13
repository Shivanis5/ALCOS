from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


class MT707PDFService:

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_pdf(self, data):

        output_dir = Path("generated/pdf")
        output_dir.mkdir(parents=True, exist_ok=True)

        amendment_number = data.get("20", "UNKNOWN")

        pdf_path = output_dir / f"{amendment_number}_MT707.pdf"

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        story = []

        doc.build(story)

        return pdf_path