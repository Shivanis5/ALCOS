from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QLineEdit,
    QMessageBox,
)

from app.core.context import get_context
from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage, StageStatus
from app.services.lc_workflow_service import LCWorkflowService


class LCIntakeWidget(QWidget):
    """
    Stage 1 of the ALCOS workflow.

    This page acts as the business-facing entry point for:
    - General LC information
    - OCR / AI extraction
    - MT700 details

    Existing widgets remain separate and are opened through signals.
    """

    openGeneral = Signal()
    openOCR = Signal()
    openMT700 = Signal()

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.workflow = LCWorkflowService(self.db)
        self.context = get_context()

        self.context.currentLCChanged.connect(
            self._on_context_lc_changed
        )

        self.context.currentLCCleared.connect(
            self._on_context_lc_cleared
        )

        self.setup_ui()

        if self.context.has_lc:
            self.lc_number_input.setText(
                self.context.current_lc_number
            )

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Stage 1 — LC Intake")
        title.setStyleSheet(
            "font-size: 24px; font-weight: 700;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Receive the Letter of Credit, extract its contents, "
            "verify the information and review the MT700 data."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            "font-size: 14px; color: #555;"
        )
        layout.addWidget(subtitle)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)

        info = QLabel(
            "Complete the following intake activities for the same LC:"
        )
        info.setStyleSheet(
            "font-size: 15px; font-weight: 600;"
        )
        layout.addWidget(info)

        self.general_button = QPushButton(
            "1. Review / Enter General LC Information"
        )
        self.general_button.setMinimumHeight(48)
        self.general_button.clicked.connect(
            self.openGeneral.emit
        )
        layout.addWidget(self.general_button)

        self.ocr_button = QPushButton(
            "2. Upload LC and Run OCR + AI Extraction"
        )
        self.ocr_button.setMinimumHeight(48)
        self.ocr_button.clicked.connect(
            self.openOCR.emit
        )
        layout.addWidget(self.ocr_button)

        self.mt700_button = QPushButton(
            "3. Review MT700 / LC Message Details"
        )
        self.mt700_button.setMinimumHeight(48)
        self.mt700_button.clicked.connect(
            self.openMT700.emit
        )
        layout.addWidget(self.mt700_button)

        completion_title = QLabel(
            "Complete Stage 1"
        )
        completion_title.setStyleSheet(
            "font-size: 15px; "
            "font-weight: 600; "
            "margin-top: 14px;"
        )
        layout.addWidget(completion_title)

        self.lc_number_input = QLineEdit()
        self.lc_number_input.setPlaceholderText(
            "Enter saved LC Number"
        )
        self.lc_number_input.setMinimumHeight(38)
        layout.addWidget(self.lc_number_input)

        self.complete_button = QPushButton(
            "Complete LC Intake → Continue to PO Matching"
        )
        self.complete_button.setMinimumHeight(48)
        self.complete_button.clicked.connect(
            self.complete_intake
        )
        layout.addWidget(self.complete_button)

        note = QLabel(
            "Stage 1 is complete only after the LC information "
            "has been received, extracted and verified."
        )
        note.setWordWrap(True)
        note.setStyleSheet(
            "margin-top: 14px; color: #666;"
        )
        layout.addWidget(note)

        layout.addStretch()

    def _on_context_lc_changed(self, lc_id: int, lc_number: str):
        """Synchronize the LC field with the shared context."""
        self.lc_number_input.setText(lc_number)

    def _on_context_lc_cleared(self):
        """Drop the LC reference so actions cannot hit a stale LC."""
        self.lc_number_input.clear()

    def _operator(self) -> str:
        """Authenticated operator for workflow history records."""
        return self.context.current_user or "USER"

    def complete_intake(self):
        lc_number = self.lc_number_input.text().strip()

        if not lc_number:
            QMessageBox.warning(
                self,
                "LC Intake",
                "Enter the saved LC Number.",
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
                "LC Intake",
                f"LC {lc_number} was not found.\n\n"
                "Save it in General Information first.",
            )
            return

        lc_id = int(lc["id"])

        workflow = self.workflow.get_workflow(lc_id)

        if workflow is None:
            QMessageBox.critical(
                self,
                "LC Intake",
                "No workflow exists for this LC.",
            )
            return

        current_stage = int(
            workflow["current_stage"]
        )

        if current_stage == int(
            LCStage.PO_MATCHING
        ):
            QMessageBox.information(
                self,
                "LC Intake",
                "Stage 1 is already complete.\n\n"
                "This LC is ready for PO Matching.",
            )
            return

        if current_stage != int(
            LCStage.INTAKE
        ):
            QMessageBox.warning(
                self,
                "LC Intake",
                "This LC has already progressed "
                "beyond the Intake stage.",
            )
            return

        try:
            self.workflow.record_stage_event(
                lc_id,
                LCStage.INTAKE,
                StageStatus.COMPLETED,
                action="INTAKE_VERIFIED",
                notes=(
                    "LC intake completed after "
                    "user verification."
                ),
                performed_by=self._operator(),
            )

            self.workflow.transition_stage(
                lc_id,
                LCStage.PO_MATCHING,
                action="INTAKE_TO_PO_MATCHING",
                notes=(
                    "LC released from Intake "
                    "to PO Matching."
                ),
                performed_by=self._operator(),
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "LC Intake Error",
                str(exc),
            )
            return

        self._refresh_lc_context(lc_id)

        QMessageBox.information(
            self,
            "LC Intake Complete",
            f"{lc_number} completed Stage 1.\n\n"
            "Current Stage: 2 — PO Matching",
        )

    def _refresh_lc_context(self, lc_id: int):
        """Publish the new workflow position to the shared context."""
        if self.context.current_lc_id != lc_id:
            return

        workflow = self.workflow.get_workflow(lc_id)

        if workflow is None:
            return

        self.context.update_lc_metadata(
            {
                "current_stage": int(
                    workflow["current_stage"]
                ),
                "stage_status": workflow["stage_status"],
                "overall_status": workflow["overall_status"],
            }
        )

