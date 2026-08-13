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

class MT700PDFService:

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_pdf(self, data):

        output_dir = Path("generated/pdf")
        output_dir.mkdir(parents=True, exist_ok=True)

        lc_number = data.get("20", "UNKNOWN")

        pdf_path = output_dir / f"{lc_number}_MT700.pdf"

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        story = []

        # =====================================================
        # BANK HEADER
        # =====================================================

        title = Paragraph(
            "<b><font size=18 color='darkblue'>ALCOS BANKING OPERATING SYSTEM</font></b>",
            self.styles["Title"],
        )

        subtitle = Paragraph(
            "<b>Trade Finance Division</b>",
            self.styles["Heading2"],
        )

        swift = Paragraph(
            "<b>SWIFT MESSAGE TYPE : MT700</b>",
            self.styles["Heading3"],
        )

        story.append(title)
        story.append(subtitle)
        story.append(swift)
        story.append(Spacer(1, 10))

        # =====================================================
        # DOCUMENTARY CREDIT INFORMATION
        # =====================================================

        info = [

            ["Field", "Value"],

            [":20: Documentary Credit Number", data.get("20", "")],

            [":27: Sequence of Total", data.get("27", "")],

            [":40A: Form of Documentary Credit", data.get("40A", "")],

            [":31C: Date of Issue", data.get("31C", "")],

            [":31D: Date & Place of Expiry", data.get("31D", "")],

        ]

        table = Table(info, colWidths=[90 * mm, 80 * mm])

        table.setStyle(TableStyle([

            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),

            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

            ("BACKGROUND", (0, 1), (0, -1), colors.whitesmoke),

            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

            ("TOPPADDING", (0, 0), (-1, -1), 6),

        ]))

        story.append(table)

        story.append(Spacer(1, 12))

        # We will build the PDF section by section

        title_style = self.styles["Title"]

story.append(
    Paragraph(
        "ALCOS BANKING OPERATING SYSTEM",
        title_style,
    )
)

story.append(
    Paragraph(
        "Trade Finance Division",
        self.styles["Heading2"],
    )
)

story.append(Spacer(1, 6))

story.append(
    Paragraph(
        "<b>SWIFT MT700</b>",
        self.styles["Heading1"],
    )
)

story.append(
    Paragraph(
        "Issue of a Documentary Credit",
        self.styles["Normal"],
    )
)

story.append(Spacer(1, 12))


story.append(
    Paragraph(
        "<b>SWIFT MESSAGE</b>",
        self.styles["Heading2"],
    )
)

story.append(Spacer(1, 8))

story.append(Spacer(1, 10))

        swift_rows = [

            [":20:", data.get("20", "")],

            [":27:", data.get("27", "")],

            [":40A:", data.get("40A", "")],

            [":31C:", data.get("31C", "")],

            [":31D:", data.get("31D", "")],

            [":50:", data.get("50", "")],

            [":59:", data.get("59", "")],

            [":32B:", data.get("32B", "")],

            [":39A:", data.get("39A", "")],

            [":43P:", data.get("43P", "")],

            [":43T:", data.get("43T", "")],

            [":44A:", data.get("44A", "")],

            [":44B:", data.get("44B", "")],

            [":44C:", data.get("44C", "")],

            [":44E:", data.get("44E", "")],

            [":44F:", data.get("44F", "")],

            [":45A:", data.get("45A", "")],

            [":46A:", data.get("46A", "")],

            [":47A:", data.get("47A", "")],

        ]

        swift_table = Table(
            swift_rows,
            colWidths=[25*mm, 145*mm]
        )

        swift_table.setStyle(TableStyle([

            ("GRID",(0,0),(-1,-1),0.3,colors.grey),

            ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

            ("VALIGN",(0,0),(-1,-1),"TOP"),

            ("BOTTOMPADDING",(0,0),(-1,-1),5),

            ("TOPPADDING",(0,0),(-1,-1),5),

        ]))

        story.append(swift_table)

        doc.build(story)

        return pdf_path