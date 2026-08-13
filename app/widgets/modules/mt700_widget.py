from __future__ import annotations

from PySide6.QtCore import QDate

from app.services.mt700_service import MT700Service
from app.services.swift_service import SwiftService
from app.services.mt700_pdf_service import MT700PDFService
from app.services.email_service import EmailService

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
    QGridLayout,
    QHBoxLayout,
    QMessageBox,
    
)


class MT700Widget(QWidget):
    """
    MT700 Documentary Credit
    """

    def __init__(self):
        super().__init__()

        self.mt700_service = MT700Service()

        self.swift_service = SwiftService()

        self.pdf_service = MT700PDFService()

        self.email_service = EmailService()

        self.current_lc = None

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        
        ###################################################
        # Title
        ###################################################

        title = QLabel("MT700 Documentary Credit")

        title.setObjectName("sectionTitle")

        main_layout.addWidget(title)

        ###################################################
        # Credit Information
        ###################################################

        credit_group = QGroupBox("Credit Information")

        credit_form = QFormLayout()

        self.field27 = QLineEdit("1/1")

        self.field40A = QComboBox()
        self.field40A.addItems([
            "IRREVOCABLE",
            "REVOCABLE"
        ])

        self.field20 = QLineEdit()

        self.field31C = QDateEdit()
        self.field31C.setCalendarPopup(True)
        self.field31C.setDate(QDate.currentDate())

        self.field31D = QDateEdit()
        self.field31D.setCalendarPopup(True)
        self.field31D.setDate(QDate.currentDate().addDays(90))

        credit_form.addRow("27 Sequence", self.field27)
        credit_form.addRow("40A Form of Credit", self.field40A)
        credit_form.addRow("20 LC Reference", self.field20)
        credit_form.addRow("31C Issue Date", self.field31C)
        credit_form.addRow("31D Expiry Date", self.field31D)

        credit_group.setLayout(credit_form)

        ###################################################
        # Applicant
        ###################################################

        applicant_group = QGroupBox("Applicant")

        applicant_form = QFormLayout()

        self.field50 = QTextEdit()

        applicant_form.addRow("50 Applicant", self.field50)

        applicant_group.setLayout(applicant_form)

        ###################################################
        # Beneficiary
        ###################################################

        beneficiary_group = QGroupBox("Beneficiary")

        beneficiary_form = QFormLayout()

        self.field59 = QTextEdit()

        beneficiary_form.addRow("59 Beneficiary", self.field59)

        beneficiary_group.setLayout(beneficiary_form)

        ###################################################
        # Amount
        ###################################################

        amount_group = QGroupBox("Amount")

        amount_form = QFormLayout()

        self.currency = QComboBox()
        self.currency.addItems([
            "USD",
            "EUR",
            "GBP",
            "INR",
            "JPY",
            "AED",
        ])

        self.amount = QLineEdit()

        self.field39A = QLineEdit()

        amount_form.addRow("Currency", self.currency)
        amount_form.addRow("Amount", self.amount)
        amount_form.addRow("39A Tolerance", self.field39A)

        amount_group.setLayout(amount_form)

        ###################################################
        # Shipment
        ###################################################

        shipment_group = QGroupBox("Shipment")

        shipment_form = QFormLayout()

        self.field43P = QComboBox()
        self.field43P.addItems(["ALLOWED", "NOT ALLOWED"])

        self.field43T = QComboBox()
        self.field43T.addItems(["ALLOWED", "NOT ALLOWED"])

        self.field44A = QLineEdit()
        self.field44B = QLineEdit()
        self.field44C = QDateEdit()
        self.field44C.setCalendarPopup(True)

        self.field44E = QLineEdit()
        self.field44F = QLineEdit()

        shipment_form.addRow("43P Partial Shipment", self.field43P)
        shipment_form.addRow("43T Transshipment", self.field43T)
        shipment_form.addRow("44A Place of Receipt", self.field44A)
        shipment_form.addRow("44B Final Destination", self.field44B)
        shipment_form.addRow("44C Latest Shipment", self.field44C)
        shipment_form.addRow("44E Port of Loading", self.field44E)
        shipment_form.addRow("44F Port of Discharge", self.field44F)

        shipment_group.setLayout(shipment_form)

        ###################################################
        # Goods
        ###################################################

        goods_group = QGroupBox("Goods")

        goods_layout = QVBoxLayout()

        self.field45A = QTextEdit()

        goods_layout.addWidget(self.field45A)

        goods_group.setLayout(goods_layout)

        ###################################################
        # Documents
        ###################################################

        documents_group = QGroupBox("Required Documents")

        documents_layout = QVBoxLayout()

        self.field46A = QTextEdit()

        documents_layout.addWidget(self.field46A)

        documents_group.setLayout(documents_layout)

        ###################################################
        # Additional Conditions
        ###################################################

        conditions_group = QGroupBox("Additional Conditions")

        conditions_layout = QVBoxLayout()

        self.field47A = QTextEdit()

        conditions_layout.addWidget(self.field47A)

        conditions_group.setLayout(conditions_layout)

        ###################################################
        # Grid
        ###################################################

        grid = QGridLayout()

        grid.addWidget(credit_group, 0, 0)
        grid.addWidget(amount_group, 0, 1)

        grid.addWidget(applicant_group, 1, 0)
        grid.addWidget(beneficiary_group, 1, 1)

        grid.addWidget(shipment_group, 2, 0, 1, 2)

        main_layout.addLayout(grid)

        main_layout.addWidget(goods_group)
        main_layout.addWidget(documents_group)
        main_layout.addWidget(conditions_group)

        ###################################################
        # Buttons
        ###################################################

        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save MT700")
        self.save_button.clicked.connect(
            self.save_mt700
        )


        self.load_button = QPushButton("Load MT700")
        self.load_button.clicked.connect(
            self.load_mt700
        )

        self.swift_button = QPushButton("Generate SWIFT")

        self.swift_button.clicked.connect(
            self.generate_swift
        )

        self.pdf_button = QPushButton("Generate PDF")

        self.pdf_button.clicked.connect(
            self.generate_pdf
        )

        button_layout.addStretch()

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.swift_button)
        button_layout.addWidget(self.pdf_button)

        main_layout.addLayout(button_layout)

        main_layout.addStretch()

        ####################################################
        # Save MT700
        ####################################################

    def save_mt700(self):

        self.mt700_service.save_mt700(

        self.field20.text(),

        self.field27.text(),

        self.field40A.currentText(),

        self.field20.text(),

        self.field31C.date().toString("yyyy-MM-dd"),

        self.field31D.date().toString("yyyy-MM-dd"),

        self.field50.toPlainText(),

        self.field59.toPlainText(),

        f"{self.currency.currentText()} {self.amount.text()}",

        self.field39A.text(),

        "",

        "",

        self.field43P.currentText(),

        self.field43T.currentText(),

        self.field44A.text(),

        self.field44B.text(),

        self.field44C.date().toString("yyyy-MM-dd"),

        self.field44E.text(),

        self.field44F.text(),

        self.field45A.toPlainText(),

        self.field46A.toPlainText(),

        self.field47A.toPlainText(),

        "",

        "",

        "",

        "",

        "",

        "",
        )

        QMessageBox.information(
            self,
            "Success",
            "MT700 saved successfully."
        )
            
        ####################################################
        # Load MT700
        ####################################################

    def load_mt700(self):
        lc_number = self.field20.text().strip()

        if not lc_number:

            QMessageBox.warning(
               self,
               "Missing LC Number",
               "Please enter LC Reference (Field 20)."
            )

            return

        print(lc_number)

    ####################################################
    # Generate PDF
    ####################################################

    def generate_pdf(self):

        lc_number = self.field20.text().strip()

        if not lc_number:
            QMessageBox.warning(
                self,
                "Missing LC Number",
                "Please enter LC Reference (Field 20)."
            )
            return

        data = {

            "20": self.field20.text(),

            "27": self.field27.text(),

            "40A": self.field40A.currentText(),

            "31C": self.field31C.date().toString("dd-MMM-yyyy"),

            "31D": self.field31D.date().toString("dd-MMM-yyyy"),

            "50": self.field50.toPlainText(),

            "59": self.field59.toPlainText(),

            "32B": f"{self.currency.currentText()} {self.amount.text()}",

            "39A": self.field39A.text(),

            "43P": self.field43P.currentText(),

            "43T": self.field43T.currentText(),

            "44A": self.field44A.text(),

            "44B": self.field44B.text(),

            "44C": self.field44C.date().toString("dd-MMM-yyyy"),

            "44E": self.field44E.text(),

            "44F": self.field44F.text(),

            "45A": self.field45A.toPlainText(),

            "46A": self.field46A.toPlainText(),

            "47A": self.field47A.toPlainText(),


        }

        pdf_path = self.pdf_service.generate_pdf(data)

        QMessageBox.information(
            self,
            "PDF Generated",
            f"PDF created successfully.\n\n{pdf_path}"
        )

    ####################################################
    # Generate SWIFT
    ####################################################

    def generate_swift(self):

        QMessageBox.information(
            self,
            "Generate SWIFT",
            "Generate SWIFT button clicked."
        )