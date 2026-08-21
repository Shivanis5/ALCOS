from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from app.core.context import get_context
from app.core.database import DatabaseManager
from app.services.discrepancy_service import DiscrepancyService


class DiscrepancyWidget(QWidget):

    openMT707 = Signal()

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.service = DiscrepancyService(self.db)
        self.context = get_context()

        self.current_lc_id = None
        self.current_rows = []

        self.context.currentLCChanged.connect(
            self._on_context_lc_changed
        )

        self.context.currentLCCleared.connect(
            self._on_context_lc_cleared
        )

        self.setup_ui()

        if self.context.has_lc:
            self.lc_number.setText(
                self.context.current_lc_number
            )

    def _on_context_lc_changed(self, lc_id: int, lc_number: str):
        """Synchronize with the shared context; drop stale rows."""
        self.lc_number.setText(lc_number)
        self.current_lc_id = None
        self.current_rows = []
        self.table.setRowCount(0)

    def _on_context_lc_cleared(self):
        """Clear the LC reference so actions cannot hit a stale LC."""
        self.lc_number.clear()
        self.current_lc_id = None
        self.current_rows = []
        self.table.setRowCount(0)

    def _operator(self) -> str:
        """Authenticated operator for audit records."""
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
            "Stage 4 — Discrepancy Review"
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: 700;"
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Record discrepancies requiring amendment and "
            "prepare the corrected wording for MT707."
        )

        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.lc_number = QLineEdit()

        self.lc_number.setPlaceholderText(
            "Enter LC Number"
        )

        self.lc_number.setMinimumHeight(38)

        layout.addWidget(
            self.lc_number
        )

        details_group = QGroupBox(
            "Discrepancy Details"
        )

        form = QFormLayout(
            details_group
        )

        self.discrepancy_type = QComboBox()

        self.discrepancy_type.addItems(
            [
                "CLAUSE",
                "AMOUNT",
                "DATE",
                "DOCUMENT",
                "SHIPMENT",
                "PARTY",
                "OTHER",
            ]
        )

        form.addRow(
            "Discrepancy Type:",
            self.discrepancy_type,
        )

        self.severity = QComboBox()

        self.severity.addItems(
            [
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            ]
        )

        form.addRow(
            "Severity:",
            self.severity,
        )

        self.field_reference = QLineEdit()

        self.field_reference.setPlaceholderText(
            "Example: 44C / Latest Shipment Date"
        )

        form.addRow(
            "LC Field / Clause:",
            self.field_reference,
        )

        self.current_text = QTextEdit()
        self.current_text.setMaximumHeight(80)

        form.addRow(
            "Current LC Text:",
            self.current_text,
        )

        self.required_text = QTextEdit()
        self.required_text.setMaximumHeight(80)

        form.addRow(
            "Required / Correct Text:",
            self.required_text,
        )

        self.reason = QTextEdit()
        self.reason.setMaximumHeight(80)

        form.addRow(
            "Reason:",
            self.reason,
        )

        layout.addWidget(
            details_group
        )

        buttons = QHBoxLayout()

        self.save_button = QPushButton(
            "Save Discrepancy"
        )

        self.save_button.clicked.connect(
            self.save_discrepancy
        )

        buttons.addWidget(
            self.save_button
        )

        self.refresh_button = QPushButton(
            "Refresh"
        )

        self.refresh_button.clicked.connect(
            self.load_discrepancies
        )

        buttons.addWidget(
            self.refresh_button
        )

        self.resolve_button = QPushButton(
            "Resolve Selected"
        )

        self.resolve_button.clicked.connect(
            self.resolve_selected
        )

        buttons.addWidget(
            self.resolve_button
        )

        self.mt707_button = QPushButton(
            "Prepare Amendment / Open MT707"
        )

        self.mt707_button.clicked.connect(
            self.openMT707.emit
        )

        buttons.addWidget(
            self.mt707_button
        )

        layout.addLayout(buttons)

        self.status_label = QLabel(
            "Enter an LC currently in Stage 4."
        )

        self.status_label.setWordWrap(True)

        layout.addWidget(
            self.status_label
        )

        self.table = QTableWidget(
            0,
            6,
        )

        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Type",
                "Severity",
                "Field / Clause",
                "Status",
                "Reason",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.table
        )

    def get_lc_id(self):
        lc_number = (
            self.lc_number.text().strip()
        )

        if not lc_number:
            QMessageBox.warning(
                self,
                "Discrepancy",
                "Enter an LC Number.",
            )
            return None

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
                "Discrepancy",
                f"LC {lc_number} was not found.",
            )
            return None

        self.current_lc_id = int(
            lc["id"]
        )

        return self.current_lc_id

    def save_discrepancy(self):
        lc_id = self.get_lc_id()

        if lc_id is None:
            return

        try:
            discrepancy_id = (
                self.service.create_discrepancy(
                    lc_id,
                    discrepancy_type=(
                        self.discrepancy_type.currentText()
                    ),
                    severity=(
                        self.severity.currentText()
                    ),
                    field_reference=(
                        self.field_reference.text().strip()
                        or None
                    ),
                    current_text=(
                        self.current_text
                        .toPlainText()
                        .strip()
                        or None
                    ),
                    required_text=(
                        self.required_text
                        .toPlainText()
                        .strip()
                        or None
                    ),
                    reason=(
                        self.reason
                        .toPlainText()
                        .strip()
                        or None
                    ),
                    created_by=self._operator(),
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Discrepancy Error",
                str(exc),
            )
            return

        self.status_label.setText(
            f"Discrepancy #{discrepancy_id} saved."
        )

        self.load_discrepancies()

        QMessageBox.information(
            self,
            "Discrepancy",
            "Discrepancy saved successfully.",
        )

    def load_discrepancies(self):
        lc_id = self.get_lc_id()

        if lc_id is None:
            return

        try:
            self.current_rows = (
                self.service.list_discrepancies(
                    lc_id
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Discrepancy Error",
                str(exc),
            )
            return

        self.table.setRowCount(
            len(self.current_rows)
        )

        for row_index, row in enumerate(
            self.current_rows
        ):
            values = [
                row["id"],
                row["discrepancy_type"],
                row["severity"],
                row["field_reference"] or "",
                row["status"],
                row["reason"] or "",
            ]

            for column, value in enumerate(
                values
            ):
                self.table.setItem(
                    row_index,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

        self.status_label.setText(
            f"{len(self.current_rows)} "
            "discrepancy record(s) loaded."
        )

    def resolve_selected(self):
        row_index = self.table.currentRow()

        if row_index < 0:
            QMessageBox.warning(
                self,
                "Discrepancy",
                "Select a discrepancy first.",
            )
            return

        item = self.table.item(
            row_index,
            0,
        )

        if item is None:
            return

        discrepancy_id = int(
            item.text()
        )

        try:
            self.service.resolve_discrepancy(
                discrepancy_id
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Discrepancy Error",
                str(exc),
            )
            return

        self.load_discrepancies()

        QMessageBox.information(
            self,
            "Discrepancy",
            "Selected discrepancy resolved.",
        )
