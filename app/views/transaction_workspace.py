from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
)

from app.widgets.transaction_sidebar import (
    TransactionSidebar,
)

from app.widgets.transaction_header import (
    TransactionHeader,
)

from app.widgets.modules.general_information_widget import (
    GeneralInformationWidget,
)

from app.widgets.modules.lc_intake_widget import (
    LCIntakeWidget,
)

from app.widgets.modules.po_matching_widget import (
    POMatchingWidget,
)

from app.widgets.modules.scrutiny_widget import (
    ScrutinyWidget,
)

from app.widgets.modules.amendments_widget import (
    AmendmentsWidget,
)

from app.widgets.modules.mt700_widget import (
    MT700Widget,
)

from app.widgets.modules.mt707_widget import (
    MT707Widget,
)

from app.widgets.modules.documents_widget import (
    DocumentsWidget,
)

from app.widgets.modules.ocr_widget import (
    OCRWidget,
)

from app.widgets.modules.validation_widget import (
    ValidationWidget,
)

from app.widgets.modules.discrepancy_widget import (
    DiscrepancyWidget,
)

from app.widgets.modules.risk_widget import (
    RiskWidget,
)

from app.widgets.modules.compliance_widget import (
    ComplianceWidget,
)

from app.widgets.modules.pdf_widget import (
    PDFWidget,
)

from app.widgets.modules.email_widget import (
    EmailWidget,
)


class TransactionWorkspace(QWidget):
    """
    Main Trade Transaction Workspace.
    """

    def __init__(self):
        super().__init__()

        self.setup_ui()

    ##################################################
    # UI
    ##################################################

    def setup_ui(self):

        self.setWindowTitle("ALCOS Trade Transaction")

        self.showMaximized()

        ##################################################
        # Main Layout
        ##################################################

        main_layout = QHBoxLayout(self)

        ##################################################
        # Sidebar
        ##################################################

        self.sidebar = TransactionSidebar()

        main_layout.addWidget(self.sidebar)

        ##################################################
        # Right Workspace
        ##################################################

        right_layout = QVBoxLayout()

        self.header = TransactionHeader()

        right_layout.addWidget(self.header)

        ##################################################
        # Module Stack
        ##################################################

        self.stack = QStackedWidget()

        ##################################################
        # Create Modules
        ##################################################

        self.general_widget = GeneralInformationWidget()

        self.lc_intake_widget = LCIntakeWidget()

        self.po_matching_widget = POMatchingWidget()

        self.scrutiny_widget = ScrutinyWidget()

        self.amendments_widget = AmendmentsWidget()

        self.mt700_widget = MT700Widget()

        self.mt707_widget = MT707Widget()

        self.documents_widget = DocumentsWidget()

        self.ocr_widget = OCRWidget()

        self.validation_widget = ValidationWidget()

        self.discrepancy_widget = DiscrepancyWidget()

        self.risk_widget = RiskWidget()

        self.compliance_widget = ComplianceWidget()

        self.pdf_widget = PDFWidget()

        self.email_widget = EmailWidget()

        ##################################################
        # Add Modules to Stack
        ##################################################

        self.stack.addWidget(self.general_widget)

        self.stack.addWidget(self.lc_intake_widget)

        self.stack.addWidget(self.po_matching_widget)

        self.stack.addWidget(self.scrutiny_widget)

        self.stack.addWidget(self.amendments_widget)

        self.stack.addWidget(self.mt700_widget)

        self.stack.addWidget(self.mt707_widget)

        self.stack.addWidget(self.documents_widget)

        self.stack.addWidget(self.ocr_widget)

        self.stack.addWidget(self.validation_widget)

        self.stack.addWidget(self.discrepancy_widget)

        self.stack.addWidget(self.risk_widget)

        self.stack.addWidget(self.compliance_widget)

        self.stack.addWidget(self.pdf_widget)

        self.stack.addWidget(self.email_widget)

        ##################################################
        # Default Module
        ##################################################

        self.stack.setCurrentWidget(
            self.general_widget
        )

        right_layout.addWidget(self.stack)

        ##################################################
        # Assemble Layout
        ##################################################

        main_layout.addLayout(right_layout)

        ##################################################
        # Signal Connections
        ##################################################

        self.sidebar.moduleSelected.connect(
            self.load_module
        )

        self.lc_intake_widget.openGeneral.connect(
            lambda: self.stack.setCurrentWidget(
                self.general_widget
            )
        )

        self.lc_intake_widget.openOCR.connect(
            lambda: self.stack.setCurrentWidget(
                self.ocr_widget
            )
        )

        self.lc_intake_widget.openMT700.connect(
            lambda: self.stack.setCurrentWidget(
                self.mt700_widget
            )
        )

        self.scrutiny_widget.openValidation.connect(
            lambda: self.stack.setCurrentWidget(
                self.validation_widget
            )
        )

        self.scrutiny_widget.openRisk.connect(
            lambda: self.stack.setCurrentWidget(
                self.risk_widget
            )
        )

        self.scrutiny_widget.openCompliance.connect(
            lambda: self.stack.setCurrentWidget(
                self.compliance_widget
            )
        )

        self.amendments_widget.openDiscrepancy.connect(
            lambda: self.stack.setCurrentWidget(
                self.discrepancy_widget
            )
        )

        self.amendments_widget.openMT707.connect(
            lambda: self.stack.setCurrentWidget(
                self.mt707_widget
            )
        )

        self.discrepancy_widget.openMT707.connect(
            lambda: self.stack.setCurrentWidget(
                self.mt707_widget
            )
        )

    ##################################################
    # Module Navigation
    ##################################################

    def load_module(self, module_name: str):

        pages = {

            "general": self.general_widget,

            "intake": self.lc_intake_widget,

            "po_matching": self.po_matching_widget,

            "scrutiny": self.scrutiny_widget,

            "amendments": self.amendments_widget,

            "mt700": self.mt700_widget,

            "mt707": self.mt707_widget,

            "documents": self.documents_widget,

            "ocr": self.ocr_widget,

            "validation": self.validation_widget,

            "discrepancy": self.discrepancy_widget,

            "risk": self.risk_widget,

            "compliance": self.compliance_widget,

            "pdf": self.pdf_widget,

            "email": self.email_widget,

        }

        widget = pages.get(module_name)

        if widget is not None:

            self.stack.setCurrentWidget(widget)