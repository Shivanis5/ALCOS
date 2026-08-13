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

    ##################################################
    # Module Navigation
    ##################################################

    def load_module(self, module_name: str):

        pages = {

            "general": self.general_widget,

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