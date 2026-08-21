from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.core.context import get_context
from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage, StageStatus
from app.services.lc_workflow_service import (
    LCWorkflowService,
)


class AmendmentsWidget(QWidget):
    """
    Stage 4 - Amendments.

    Business-facing orchestration for:
    - discrepancies
    - amendment / MT707 preparation
    - receipt of amended LC
    - mandatory return to Scrutiny
    """

    openDiscrepancy = Signal()
    openMT707 = Signal()

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

    def _on_context_lc_changed(self, lc_id: int, lc_number: str):
        """Synchronize the LC field with the shared context."""
        self.lc_number_input.setText(lc_number)

    def _on_context_lc_cleared(self):
        """Clear the LC reference so actions cannot hit a stale LC."""
        self.lc_number_input.clear()

    def _operator(self) -> str:
        """Authenticated operator for workflow history records."""
        return self.context.current_user or "USER"

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            28,
            28,
            28,
            28,
        )

        layout.setSpacing(14)

        title = QLabel(
            "Stage 4 — Amendments"
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: 700;"
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Resolve discrepancies, prepare the amendment request / "
            "MT707 and return the amended LC to Scrutiny."
        )

        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        self.lc_number_input = QLineEdit()

        self.lc_number_input.setPlaceholderText(
            "Enter LC Number"
        )

        self.lc_number_input.setMinimumHeight(
            38
        )

        layout.addWidget(
            self.lc_number_input
        )

        tools_group = QGroupBox(
            "Amendment Activities"
        )

        tools_layout = QHBoxLayout(
            tools_group
        )

        self.discrepancy_button = QPushButton(
            "Open Discrepancy"
        )

        self.discrepancy_button.clicked.connect(
            self.openDiscrepancy.emit
        )

        tools_layout.addWidget(
            self.discrepancy_button
        )

        self.mt707_button = QPushButton(
            "Open MT707 / Amendment Request"
        )

        self.mt707_button.clicked.connect(
            self.openMT707.emit
        )

        tools_layout.addWidget(
            self.mt707_button
        )

        layout.addWidget(
            tools_group
        )

        info = QLabel(
            "When the amended LC is received, confirm it below. "
            "ALCOS will complete Stage 4 and return the LC to "
            "Stage 3 for mandatory re-scrutiny."
        )

        info.setWordWrap(True)

        layout.addWidget(info)

        self.received_button = QPushButton(
            "Amended LC Received → Return to Scrutiny"
        )

        self.received_button.setMinimumHeight(
            48
        )

        self.received_button.clicked.connect(
            self.amended_lc_received
        )

        layout.addWidget(
            self.received_button
        )

        self.status_label = QLabel(
            "Enter an LC currently in Stage 4."
        )

        self.status_label.setWordWrap(True)

        layout.addWidget(
            self.status_label
        )

        layout.addStretch()

    def amended_lc_received(self):
        lc_number = (
            self.lc_number_input
            .text()
            .strip()
        )

        if not lc_number:
            QMessageBox.warning(
                self,
                "Amendments",
                "Enter an LC Number.",
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
                "Amendments",
                f"LC {lc_number} was not found.",
            )
            return

        lc_id = int(lc["id"])

        workflow = self.workflow.get_workflow(
            lc_id
        )

        if workflow is None:
            QMessageBox.critical(
                self,
                "Amendments",
                "No workflow exists for this LC.",
            )
            return

        if int(
            workflow["current_stage"]
        ) == int(
            LCStage.SCRUTINY
        ):
            QMessageBox.information(
                self,
                "Amendments",
                "This amended LC has already "
                "returned to Scrutiny.",
            )
            return

        if int(
            workflow["current_stage"]
        ) != int(
            LCStage.AMENDMENT
        ):
            QMessageBox.warning(
                self,
                "Amendments",
                f"This LC is currently at Stage "
                f"{workflow['current_stage']} "
                f"with status "
                f"{workflow['stage_status']}.",
            )
            return

        try:
            self.workflow.record_stage_event(
                lc_id,
                LCStage.AMENDMENT,
                StageStatus.COMPLETED,
                action="AMENDED_LC_RECEIVED",
                notes=(
                    "Amended LC received and "
                    "accepted for re-scrutiny."
                ),
                performed_by=self._operator(),
            )

            self.workflow.transition_stage(
                lc_id,
                LCStage.SCRUTINY,
                action="AMENDMENT_TO_RE_SCRUTINY",
                notes=(
                    "Amended LC returned to "
                    "Stage 3 Scrutiny."
                ),
                performed_by=self._operator(),
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Amendment Error",
                str(exc),
            )
            return

        current = self.workflow.get_workflow(
            lc_id
        )

        if self.context.current_lc_id == lc_id and current is not None:
            self.context.update_lc_metadata(
                {
                    "current_stage": int(
                        current["current_stage"]
                    ),
                    "stage_status": current["stage_status"],
                    "overall_status": current["overall_status"],
                }
            )

        self.status_label.setText(
            f"{lc_number}: amended LC received | "
            f"Current Stage "
            f"{current['current_stage']} | "
            f"{current['stage_status']}"
        )

        QMessageBox.information(
            self,
            "Amendment Complete",
            f"{lc_number} completed Stage 4.\n\n"
            "The amended LC has returned to "
            "Stage 3 — Scrutiny.",
        )
