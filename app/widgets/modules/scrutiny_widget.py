from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QTextEdit,
    QMessageBox,
)

from app.core.context import get_context
from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage
from app.services.lc_workflow_service import (
    LCWorkflowService,
)
from app.services.scrutiny_service import (
    ScrutinyService,
)


class ScrutinyWidget(QWidget):
    """
    Stage 3 - Scrutiny.

    Business-facing orchestration page for:
    - Validation
    - Risk
    - Compliance
    - Discrepancy decision
    """

    openValidation = Signal()
    openRisk = Signal()
    openCompliance = Signal()

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()

        self.workflow = LCWorkflowService(
            self.db
        )

        self.scrutiny = ScrutinyService(
            self.db
        )

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
            "Stage 3 — Scrutiny"
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: 700;"
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Perform validation, risk and compliance "
            "checks and determine whether the LC may "
            "proceed or requires amendment."
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

        # -------------------------------------------------
        # Existing technical modules
        # -------------------------------------------------

        modules_group = QGroupBox(
            "Scrutiny Checks"
        )

        modules_layout = QHBoxLayout(
            modules_group
        )

        self.validation_button = QPushButton(
            "Open Validation"
        )

        self.validation_button.clicked.connect(
            self.openValidation.emit
        )

        modules_layout.addWidget(
            self.validation_button
        )

        self.risk_button = QPushButton(
            "Open Risk"
        )

        self.risk_button.clicked.connect(
            self.openRisk.emit
        )

        modules_layout.addWidget(
            self.risk_button
        )

        self.compliance_button = QPushButton(
            "Open Compliance"
        )

        self.compliance_button.clicked.connect(
            self.openCompliance.emit
        )

        modules_layout.addWidget(
            self.compliance_button
        )

        layout.addWidget(
            modules_group
        )

        # -------------------------------------------------
        # Final scrutiny decision
        # -------------------------------------------------

        decision_group = QGroupBox(
            "Final Scrutiny Decision"
        )

        form = QFormLayout(
            decision_group
        )

        self.validation_status = QComboBox()

        self.validation_status.addItems(
            [
                "PASSED",
                "FAILED",
            ]
        )

        form.addRow(
            "Validation Status:",
            self.validation_status,
        )

        self.risk_level = QComboBox()

        self.risk_level.addItems(
            [
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            ]
        )

        form.addRow(
            "Risk Level:",
            self.risk_level,
        )

        self.risk_score = QDoubleSpinBox()

        self.risk_score.setRange(
            0.0,
            100.0,
        )

        self.risk_score.setDecimals(2)

        self.risk_score.setValue(
            0.0
        )

        form.addRow(
            "Risk Score:",
            self.risk_score,
        )

        self.compliance_status = QComboBox()

        self.compliance_status.addItems(
            [
                "PASSED",
                "FAILED",
                "BLOCKED",
            ]
        )

        form.addRow(
            "Compliance Status:",
            self.compliance_status,
        )

        self.discrepancy_count = QSpinBox()

        self.discrepancy_count.setRange(
            0,
            999,
        )

        form.addRow(
            "Discrepancies:",
            self.discrepancy_count,
        )

        self.notes = QTextEdit()

        self.notes.setMaximumHeight(
            100
        )

        self.notes.setPlaceholderText(
            "Scrutiny notes / observations"
        )

        form.addRow(
            "Notes:",
            self.notes,
        )

        layout.addWidget(
            decision_group
        )

        self.run_button = QPushButton(
            "Run / Save Scrutiny Decision"
        )

        self.run_button.setMinimumHeight(
            48
        )

        self.run_button.clicked.connect(
            self.run_scrutiny
        )

        layout.addWidget(
            self.run_button
        )

        self.status_label = QLabel(
            "Enter an LC currently in Stage 3."
        )

        self.status_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.status_label
        )

        layout.addStretch()

    def run_scrutiny(self):
        lc_number = (
            self.lc_number_input
            .text()
            .strip()
        )

        if not lc_number:
            QMessageBox.warning(
                self,
                "Scrutiny",
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
                "Scrutiny",
                f"LC {lc_number} was not found.",
            )
            return

        lc_id = int(
            lc["id"]
        )

        workflow = self.workflow.get_workflow(
            lc_id
        )

        if workflow is None:
            QMessageBox.critical(
                self,
                "Scrutiny",
                "No workflow exists for this LC.",
            )
            return

        if int(
            workflow["current_stage"]
        ) != int(
            LCStage.SCRUTINY
        ):
            QMessageBox.warning(
                self,
                "Scrutiny",
                f"This LC is currently at Stage "
                f"{workflow['current_stage']} "
                f"with status "
                f"{workflow['stage_status']}.",
            )
            return

        try:
            result = self.scrutiny.evaluate(
                lc_id,
                validation_status=(
                    self.validation_status
                    .currentText()
                ),
                risk_level=(
                    self.risk_level
                    .currentText()
                ),
                risk_score=(
                    self.risk_score.value()
                ),
                compliance_status=(
                    self.compliance_status
                    .currentText()
                ),
                discrepancy_count=(
                    self.discrepancy_count.value()
                ),
                notes=(
                    self.notes
                    .toPlainText()
                    .strip()
                    or None
                ),
                performed_by=self._operator(),
            )

            decision = result["decision"]

            if decision == "PASSED":

                self.workflow.transition_stage(
                    lc_id,
                    LCStage.DOCUMENTS,
                    action="SCRUTINY_TO_DOCUMENTS",
                    notes=(
                        "Scrutiny passed. "
                        "LC released to documents."
                    ),
                    performed_by=self._operator(),
                )

                message = (
                    "Scrutiny PASSED.\n\n"
                    "The LC has moved to "
                    "Stage 5 — Documents."
                )

            elif decision == "AMENDMENT_REQUIRED":

                self.workflow.transition_stage(
                    lc_id,
                    LCStage.AMENDMENT,
                    action="SCRUTINY_TO_AMENDMENT",
                    notes=(
                        "Scrutiny identified issues "
                        "requiring amendment."
                    ),
                    performed_by=self._operator(),
                )

                message = (
                    "Scrutiny FAILED / discrepancies found.\n\n"
                    "The LC has moved to "
                    "Stage 4 — Amendments."
                )

            elif decision == "HUMAN_REVIEW_REQUIRED":

                message = (
                    "Scrutiny requires HUMAN REVIEW.\n\n"
                    "The LC remains in Stage 3."
                )

            else:
                message = (
                    f"Scrutiny decision: {decision}"
                )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Scrutiny Error",
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
            f"{lc_number}: "
            f"{decision} | "
            f"Current Stage "
            f"{current['current_stage']} | "
            f"{current['stage_status']}"
        )

        QMessageBox.information(
            self,
            "Scrutiny Result",
            message,
        )
