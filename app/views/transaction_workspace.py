from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.core.context import get_context
from app.core.database import DatabaseManager

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

        self.db = DatabaseManager()
        self.context = get_context()

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
        # LC Context Bar
        ##################################################

        self._build_lc_bar(right_layout)

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

        self.general_widget.continueToMT700.connect(
            lambda: self.stack.setCurrentWidget(
                self.mt700_widget
            )
        )

    ##################################################
    # LC Context Bar
    ##################################################

    def _build_lc_bar(self, parent_layout):

        bar = QHBoxLayout()

        label = QLabel("Current LC:")

        self.lc_input = QLineEdit()

        self.lc_input.setPlaceholderText(
            "Open LC by number (e.g. LC202600001)"
        )

        self.open_lc_button = QPushButton("Open LC")

        self.close_lc_button = QPushButton("Close LC")

        self.open_lc_button.clicked.connect(
            self._open_lc_from_input
        )

        self.close_lc_button.clicked.connect(
            self.context.clear_current_lc
        )

        bar.addWidget(label)
        bar.addWidget(self.lc_input, 1)
        bar.addWidget(self.open_lc_button)
        bar.addWidget(self.close_lc_button)

        parent_layout.addLayout(bar)

    def _open_lc_from_input(self):
        """Open the LC typed into the context bar."""
        lc_number = self.lc_input.text().strip()

        if not lc_number:
            QMessageBox.warning(
                self,
                "Open LC",
                "Enter an LC number to open.",
            )
            return

        lc = self.db.fetchone(
            """
            SELECT id
            FROM letters_of_credit
            WHERE lc_number = ?
            """,
            (lc_number,),
        )

        if lc is None:
            QMessageBox.warning(
                self,
                "Open LC",
                f"LC {lc_number} was not found.",
            )
            return

        self.open_for_lc(int(lc["id"]))

    def open_for_lc(self, lc_id: int):
        """
        Open an LC in the shared application context.

        Validates existence before publishing so no widget can act on a
        nonexistent LC. All stage modules synchronize through context.
        """
        lc = self.db.fetchone(
            """
            SELECT id, lc_number, applicant, beneficiary,
                   currency, amount, status, issue_date, expiry_date
            FROM letters_of_credit
            WHERE id = ?
            """,
            (int(lc_id),),
        )

        if lc is None:
            QMessageBox.warning(
                self,
                "Open LC",
                f"LC id {lc_id} does not exist.",
            )
            return

        workflow = self.db.fetchone(
            """
            SELECT current_stage, stage_status, overall_status
            FROM lc_workflow_state
            WHERE lc_id = ?
            """,
            (int(lc_id),),
        )

        metadata = {
            "applicant": lc["applicant"],
            "beneficiary": lc["beneficiary"],
            "currency": lc["currency"],
            "amount": lc["amount"],
            "status": lc["status"],
            "issue_date": lc["issue_date"],
            "expiry_date": lc["expiry_date"],
        }

        if workflow is not None:
            metadata.update(
                {
                    "current_stage": int(
                        workflow["current_stage"]
                    ),
                    "stage_status": workflow["stage_status"],
                    "overall_status": workflow["overall_status"],
                }
            )

        self.context.set_current_lc(
            int(lc["id"]),
            lc["lc_number"],
            metadata,
        )

        self.lc_input.setText(lc["lc_number"])

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