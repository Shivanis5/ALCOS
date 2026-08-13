from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


class PDFService:

    def generate_pdf(self, lc_number):

        output_dir = Path("generated/pdf")
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{lc_number}.pdf"

        c = canvas.Canvas(str(pdf_path), pagesize=A4)

        width, height = A4

        # ==================================================
        # Header
        # ==================================================

        c.setStrokeColor(colors.darkblue)
        c.setLineWidth(2)

        c.rect(15*mm, 15*mm, width-30*mm, height-30*mm)

        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.darkblue)
        c.drawCentredString(width/2, height-25*mm, "ALCOS BANKING OPERATING SYSTEM")

        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height-31*mm, "Trade Finance Division")

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height-42*mm, "DOCUMENTARY CREDIT (MT700)")

        # ==================================================
        # Credit Information
        # ==================================================

        y = height - 60*mm

        c.setFillColor(colors.black)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(25*mm, y, "Documentary Credit No")

        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y, lc_number)

        y -= 8*mm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(25*mm, y, "Issue Date")

        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y, "06-Aug-2026")

        y -= 8*mm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(25*mm, y, "Expiry Date")

        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y, "06-Nov-2026")

        y -= 15*mm

        # ==================================================
        # Applicant
        # ==================================================

        c.setFillColor(colors.lightgrey)
        c.rect(20*mm, y, 170*mm, 8*mm, fill=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(23*mm, y+2.5*mm, "Applicant")

        y -= 10*mm

        c.setFont("Helvetica", 10)

        c.drawString(25*mm, y, "ABC IMPORTS PRIVATE LIMITED")

        y -= 6*mm

        c.drawString(25*mm, y, "Mumbai, India")

        y -= 12*mm

        # ==================================================
        # Beneficiary
        # ==================================================

        c.setFillColor(colors.lightgrey)
        c.rect(20*mm, y, 170*mm, 8*mm, fill=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(23*mm, y+2.5*mm, "Beneficiary")

        y -= 10*mm

        c.setFont("Helvetica", 10)

        c.drawString(25*mm, y, "XYZ EXPORTS CO. LTD.")

        y -= 6*mm

        c.drawString(25*mm, y, "Shanghai, China")

        y -= 12*mm

        # ==================================================
        # Amount
        # ==================================================

        c.setFont("Helvetica-Bold", 11)
        c.drawString(25*mm, y, "Currency")

        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y, "USD")

        y -= 7*mm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(25*mm, y, "Amount")

        c.setFont("Helvetica", 10)
        c.drawString(90*mm, y, "250,000.00")

        y -= 12*mm

        # ==================================================
        # Goods
        # ==================================================

        c.setFillColor(colors.lightgrey)
        c.rect(20*mm, y, 170*mm, 8*mm, fill=1)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(23*mm, y+2.5*mm, "Description of Goods")

        y -= 10*mm

        c.setFont("Helvetica", 10)

        c.drawString(25*mm, y, "500 MT Hot Rolled Steel Coils")

        y -= 6*mm

        c.drawString(25*mm, y, "Packed for Export")

        y -= 12*mm

        # ==================================================
        # Documents
        # ==================================================

        c.setFillColor(colors.lightgrey)
        c.rect(20*mm, y, 170*mm, 8*mm, fill=1)

        c.setFillColor(colors.black)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(23*mm, y+2.5*mm, "Required Documents")

        y -= 10*mm

        docs = [
            "Commercial Invoice",
            "Packing List",
            "Bill of Lading",
            "Certificate of Origin",
            "Insurance Certificate",
        ]

        c.setFont("Helvetica", 10)

        for d in docs:
            c.drawString(28*mm, y, "• " + d)
            y -= 6*mm

        y -= 5*mm

        # ==================================================
        # Footer
        # ==================================================

        c.setStrokeColor(colors.darkblue)
        c.line(20*mm, 35*mm, 190*mm, 35*mm)

        c.setFont("Helvetica", 9)

        c.drawString(20*mm, 28*mm, "Subject to UCP 600")

        c.drawRightString(width-20*mm, 28*mm, "Generated by ALCOS")

        c.save()

        return pdf_path