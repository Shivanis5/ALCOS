from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)

from app.core.database import DatabaseManager
from app.services.po_matching_service import (
    POMatchingService,
)


class POMatchingWidget(QWidget):
    """
    Stage 2 - PO Matching.

    Finds the top purchase-order candidates for
    an existing LC and allows the user to select one.
    """

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.service = POMatchingService(self.db)

        self.current_lc_id = None
        self.candidates = []

        self.setup_ui()

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
            "Stage 2 — PO Matching"
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: 700;"
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Match the Letter of Credit against available "
            "purchase orders and review the top candidates."
        )

        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        search_layout = QHBoxLayout()

        self.lc_number_input = QLineEdit()

        self.lc_number_input.setPlaceholderText(
            "Enter LC Number"
        )

        search_layout.addWidget(
            self.lc_number_input
        )

        self.find_button = QPushButton(
            "Find Top PO Matches"
        )

        self.find_button.clicked.connect(
            self.find_matches
        )

        search_layout.addWidget(
            self.find_button
        )

        self.add_po_button = QPushButton(
            "Add Purchase Order"
        )

        self.add_po_button.clicked.connect(
            self.add_purchase_order
        )

        search_layout.addWidget(
            self.add_po_button
        )

        layout.addLayout(search_layout)

        self.status_label = QLabel(
            "Enter an LC number to begin PO matching."
        )

        layout.addWidget(
            self.status_label
        )

        self.table = QTableWidget(
            0,
            7,
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Rank",
                "PO Number",
                "Overall %",
                "Applicant %",
                "Beneficiary %",
                "Amount %",
                "Currency %",
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

        self.select_button = QPushButton(
            "Select Highlighted PO"
        )

        self.select_button.clicked.connect(
            self.select_po
        )

        layout.addWidget(
            self.select_button
        )

    def add_purchase_order(self):
        """
        Manual/local PO entry.

        This is the local prototype source.
        SAP/ERP integration can later populate
        the same purchase_orders table.
        """

        dialog = QDialog(self)
        dialog.setWindowTitle(
            "Add Purchase Order"
        )
        dialog.setMinimumWidth(500)

        form = QFormLayout(dialog)

        po_number = QLineEdit()
        applicant = QLineEdit()
        beneficiary = QLineEdit()
        amount = QLineEdit()
        currency = QLineEdit()
        issue_date = QLineEdit()
        delivery_date = QLineEdit()

        currency.setText("USD")

        issue_date.setPlaceholderText(
            "YYYY-MM-DD"
        )

        delivery_date.setPlaceholderText(
            "YYYY-MM-DD"
        )

        form.addRow(
            "PO Number:",
            po_number,
        )

        form.addRow(
            "Applicant / Buyer:",
            applicant,
        )

        form.addRow(
            "Beneficiary / Seller:",
            beneficiary,
        )

        form.addRow(
            "PO Amount:",
            amount,
        )

        form.addRow(
            "Currency:",
            currency,
        )

        form.addRow(
            "Issue Date:",
            issue_date,
        )

        form.addRow(
            "Delivery Date:",
            delivery_date,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            dialog.accept
        )

        buttons.rejected.connect(
            dialog.reject
        )

        form.addRow(buttons)

        if dialog.exec() != QDialog.Accepted:
            return

        number = po_number.text().strip()

        if not number:
            QMessageBox.warning(
                self,
                "Purchase Order",
                "PO Number is required.",
            )
            return

        try:
            po_amount = float(
                amount.text().strip()
            )

        except ValueError:
            QMessageBox.warning(
                self,
                "Purchase Order",
                "Enter a valid numeric PO amount.",
            )
            return

        try:
            po_id = (
                self.service.create_purchase_order(
                    po_number=number,
                    applicant=applicant.text().strip(),
                    beneficiary=beneficiary.text().strip(),
                    amount=po_amount,
                    currency=currency.text().strip().upper(),
                    issue_date=issue_date.text().strip() or None,
                    delivery_date=delivery_date.text().strip() or None,
                    status="OPEN",
                    source_system="LOCAL",
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "Purchase Order Error",
                str(exc),
            )
            return

        self.status_label.setText(
            f"Purchase Order {number} added "
            f"(ID {po_id})."
        )

        QMessageBox.information(
            self,
            "Purchase Order",
            f"PO {number} saved successfully.",
        )

    def find_matches(self):
        lc_number = (
            self.lc_number_input
            .text()
            .strip()
        )

        if not lc_number:
            QMessageBox.warning(
                self,
                "PO Matching",
                "Enter an LC number.",
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
                "PO Matching",
                f"LC {lc_number} was not found.",
            )
            return

        self.current_lc_id = int(
            lc["id"]
        )

        try:
            self.candidates = (
                self.service.find_candidates(
                    self.current_lc_id,
                    limit=3,
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "PO Matching Error",
                str(exc),
            )
            return

        self.populate_table()

        if self.candidates:
            self.status_label.setText(
                f"Top {len(self.candidates)} "
                f"candidate(s) found for "
                f"{lc_number}."
            )
        else:
            self.status_label.setText(
                "No open purchase orders found."
            )

    def populate_table(self):
        self.table.setRowCount(
            len(self.candidates)
        )

        for row, item in enumerate(
            self.candidates
        ):
            values = [
                row + 1,
                item["po_number"],
                item["match_score"],
                item["applicant_score"],
                item["beneficiary_score"],
                item["amount_score"],
                item["currency_score"],
            ]

            for column, value in enumerate(
                values
            ):
                self.table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

    def select_po(self):
        if self.current_lc_id is None:
            QMessageBox.warning(
                self,
                "PO Matching",
                "Find PO candidates first.",
            )
            return

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "PO Matching",
                "Select a PO candidate first.",
            )
            return

        candidate = self.candidates[row]

        try:
            result = self.service.select_match(
                self.current_lc_id,
                candidate["po_id"],
                performed_by="USER",
            )

        except Exception as exc:
            QMessageBox.critical(
                self,
                "PO Matching Error",
                str(exc),
            )
            return

        self.status_label.setText(
            f"Selected PO: "
            f"{result['po_number']} "
            f"({float(result['match_score']):.2f}%)"
        )

        QMessageBox.information(
            self,
            "PO Matching",
            "PO selected successfully. "
            "Stage 2 is now completed.",
        )
