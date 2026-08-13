from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
)

from PySide6.QtCore import QDate

from app.services.transaction_service import TransactionService


class GeneralInformationWidget(QWidget):
    """
    General Information Module
    """

    continueToMT700 = Signal()

    def __init__(self):
        super().__init__()

        self.transaction_service = TransactionService()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        from PySide6.QtWidgets import QGridLayout

        ###################################################
        # Title
        ###################################################

        title = QLabel("General Information")

        title.setObjectName("sectionTitle")

        main_layout.addWidget(title)

        ###################################################
        # Transaction Information
        ###################################################

        transaction_group = QGroupBox("Transaction Information")

        transaction_form = QFormLayout()

        self.transaction_id = QLineEdit("TXN000001")

        self.transaction_reference = QLineEdit()

        self.lc_number = QLineEdit("LC202600001")

        self.status = QComboBox()

        self.status.addItems([
            "Draft",
            "Pending",
            "Approved",
            "Rejected"
        ])

        transaction_form.addRow(
            "Transaction ID",
            self.transaction_id
        )

        transaction_form.addRow(
            "Transaction Reference",
            self.transaction_reference
        )

        transaction_form.addRow(
            "LC Number",
            self.lc_number
        )

        transaction_form.addRow(
            "Status",
            self.status
        )

        transaction_group.setLayout(transaction_form)

        #main_layout.addWidget(transaction_group)

        ###################################################
        # Applicant
        ###################################################

        applicant_group = QGroupBox("Applicant")

        applicant_form = QFormLayout()

        self.applicant_name = QLineEdit()

        self.applicant_address = QTextEdit()

        self.applicant_country = QLineEdit()

        applicant_form.addRow(
            "Applicant Name",
            self.applicant_name
        )

        applicant_form.addRow(
            "Applicant Address",
            self.applicant_address
        )

        applicant_form.addRow(
            "Applicant Country",
            self.applicant_country
        )

        applicant_group.setLayout(applicant_form)

        #main_layout.addWidget(applicant_group)

        ###################################################
        # Beneficiary
        ###################################################

        beneficiary_group = QGroupBox("Beneficiary")

        beneficiary_form = QFormLayout()

        self.beneficiary_name = QLineEdit()

        self.beneficiary_address = QTextEdit()

        self.beneficiary_country = QLineEdit()

        beneficiary_form.addRow(
            "Beneficiary Name",
            self.beneficiary_name
        )

        beneficiary_form.addRow(
            "Beneficiary Address",
            self.beneficiary_address
        )

        beneficiary_form.addRow(
            "Beneficiary Country",
            self.beneficiary_country
        )

        beneficiary_group.setLayout(
            beneficiary_form
        )

        #main_layout.addWidget(
        #    beneficiary_group
        #)

        ###################################################
        # Bank Information
        ###################################################

        bank_group = QGroupBox(
            "Bank Information"
        )

        bank_form = QFormLayout()

        self.issuing_bank = QLineEdit()

        self.advising_bank = QLineEdit()

        self.negotiating_bank = QLineEdit()

        bank_form.addRow(
            "Issuing Bank",
            self.issuing_bank
        )

        bank_form.addRow(
            "Advising Bank",
            self.advising_bank
        )

        bank_form.addRow(
            "Negotiating Bank",
            self.negotiating_bank
        )

        bank_group.setLayout(bank_form)

        #main_layout.addWidget(bank_group)

        ###################################################
        # LC Information
        ###################################################

        lc_group = QGroupBox(
            "LC Information"
        )

        lc_form = QFormLayout()

        self.currency = QComboBox()

        self.currency.addItems([
            "USD",
            "EUR",
            "GBP",
            "INR",
            "JPY",
            "AED"
        ])

        self.amount = QLineEdit()

        self.issue_date = QDateEdit()

        self.issue_date.setCalendarPopup(True)

        self.issue_date.setDate(
            QDate.currentDate()
        )

        self.expiry_date = QDateEdit()

        self.expiry_date.setCalendarPopup(True)

        self.expiry_date.setDate(
            QDate.currentDate().addDays(90)
        )

        self.expiry_place = QLineEdit()

        self.incoterms = QComboBox()

        self.incoterms.addItems([
            "FOB",
            "CIF",
            "CFR",
            "EXW",
            "DAP",
            "DDP"
        ])

        lc_form.addRow(
            "Currency",
            self.currency
        )

        lc_form.addRow(
            "Amount",
            self.amount
        )

        lc_form.addRow(
            "Issue Date",
            self.issue_date
        )

        lc_form.addRow(
            "Expiry Date",
            self.expiry_date
        )

        lc_form.addRow(
            "Expiry Place",
            self.expiry_place
        )

        lc_form.addRow(
            "Incoterms",
            self.incoterms
        )

        lc_group.setLayout(lc_form)

        #main_layout.addWidget(lc_group)

        ###################################################
        # Shipment
        ###################################################

        shipment_group = QGroupBox(
            "Shipment Information"
        )

        shipment_form = QFormLayout()

        self.port_loading = QLineEdit()

        self.port_discharge = QLineEdit()

        self.latest_shipment = QDateEdit()

        self.latest_shipment.setCalendarPopup(True)

        self.latest_shipment.setDate(
            QDate.currentDate().addDays(45)
        )

        shipment_form.addRow(
            "Port of Loading",
            self.port_loading
        )

        shipment_form.addRow(
            "Port of Discharge",
            self.port_discharge
        )

        shipment_form.addRow(
            "Latest Shipment Date",
            self.latest_shipment
        )

        shipment_group.setLayout(
            shipment_form
        )

        #main_layout.addWidget(
        #    shipment_group
        #)

        ###################################################
        # Goods
        ###################################################

        goods_group = QGroupBox(
            "Goods Description"
        )

        goods_layout = QVBoxLayout()

        self.goods_description = QTextEdit()

        goods_layout.addWidget(
            self.goods_description
        )

        goods_group.setLayout(
            goods_layout
        )

        #main_layout.addWidget(
        #    goods_group
        #)
    
        ###################################################
        # Arrange All Sections
        ###################################################

        grid = QGridLayout()

        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)

        grid.addWidget(transaction_group, 0, 0)
        grid.addWidget(lc_group, 0, 1)

        grid.addWidget(applicant_group, 1, 0)
        grid.addWidget(bank_group, 1, 1)

        grid.addWidget(beneficiary_group, 2, 0)
        grid.addWidget(shipment_group, 2, 1)

        main_layout.addLayout(grid)
   
        main_layout.addWidget(goods_group)

        ###################################################
        # Buttons
        ###################################################

        button_layout = QHBoxLayout()

        self.save_button = QPushButton(
            "Save Transaction"
        )

        self.save_button.clicked.connect(
            self.save_transaction
        )

        self.continue_button = QPushButton(
            "Continue to MT700"
        )

        self.continue_button.clicked.connect(
            self.continueToMT700.emit
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.save_button
        )

        button_layout.addWidget(
            self.continue_button
        )

        main_layout.addLayout(
            button_layout
        )

        main_layout.addStretch()

    ####################################################
    # Save Transaction
    ####################################################

    def save_transaction(self):

        self.transaction_service.create_transaction(

            self.transaction_id.text(),

            self.transaction_reference.text(),

            self.lc_number.text(),

            self.applicant_name.text(),

            self.beneficiary_name.text(),

            float(self.amount.text() or 0),

            self.currency.currentText(),

            self.status.currentText(),

            self.issue_date.date().toString("yyyy-MM-dd"),

            self.expiry_date.date().toString("yyyy-MM-dd"),
        )

        print("Transaction Saved")  