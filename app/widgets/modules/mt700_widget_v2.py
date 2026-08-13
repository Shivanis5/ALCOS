from __future__ import annotations

from PySide6.QtCore import QDate

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QTabWidget,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
)

from app.services.mt700_service import MT700Service
from app.services.swift_service import SwiftService
from app.services.pdf_service import PDFService
from app.services.email_service import EmailService


class MT700Widget(QWidget):

    def __init__(self):
        super().__init__()

        self.mt700_service = MT700Service()
        self.swift_service = SwiftService()
        self.pdf_service = PDFService()
        self.email_service = EmailService()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        ####################################################
        # Title
        ####################################################

        title = QLabel("MT700 - Documentary Credit")

        title.setObjectName("sectionTitle")

        main_layout.addWidget(title)

        ####################################################
        # Banking Tabs
        ####################################################

        self.tabs = QTabWidget()

        self.general_tab = QWidget()
        self.parties_tab = QWidget()
        self.financial_tab = QWidget()
        self.shipment_tab = QWidget()
        self.documents_tab = QWidget()
        self.conditions_tab = QWidget()
        self.preview_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.parties_tab, "Parties")
        self.tabs.addTab(self.financial_tab, "Financial")
        self.tabs.addTab(self.shipment_tab, "Shipment")
        self.tabs.addTab(self.documents_tab, "Documents")
        self.tabs.addTab(self.conditions_tab, "Conditions")
        self.tabs.addTab(self.preview_tab, "SWIFT Preview")
        
        main_layout.addWidget(self.tabs)

        ####################################################
        # General Tab
        ####################################################

        general_layout = QFormLayout()

        self.field20 = QLineEdit()

        self.field31C = QDateEdit()
        self.field31C.setCalendarPopup(True)
        self.field31C.setDate(QDate.currentDate())

        self.field31D = QDateEdit()
        self.field31D.setCalendarPopup(True)
        self.field31D.setDate(QDate.currentDate().addDays(90))

        self.field40A = QComboBox()

        self.field40A.addItems([
        "IRREVOCABLE",
        "REVOCABLE",
        ])

        general_layout.addRow("LC Reference", self.field20)

        general_layout.addRow("Issue Date", self.field31C)

        general_layout.addRow("Expiry Date", self.field31D)

        general_layout.addRow("Form of Credit", self.field40A)

        self.general_tab.setLayout(general_layout)

        ####################################################
        # Parties Tab
        ####################################################

        parties_layout = QFormLayout()

        self.field50 = QTextEdit()

        self.field59 = QTextEdit()

        self.issuing_bank = QLineEdit()

        self.advising_bank = QLineEdit()

        parties_layout.addRow(
            "Applicant",
            self.field50,
        )

        parties_layout.addRow(
            "Beneficiary",
            self.field59,
        )

        parties_layout.addRow(
            "Issuing Bank",
            self.issuing_bank,
        )

        parties_layout.addRow(
            "Advising Bank",
            self.advising_bank,
        )

        self.parties_tab.setLayout(parties_layout)

        ####################################################
        # Financial Tab
        ####################################################

        financial_layout = QFormLayout()

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

        self.available_with = QLineEdit()

        self.available_by = QComboBox()

        self.available_by.addItems([
            "Payment",
            "Acceptance",
            "Negotiation",
            "Deferred Payment",
        ])

        financial_layout.addRow(
            "Currency",
        self.currency, 
        )

        financial_layout.addRow(
            "Amount",
            self.amount,
        )

        financial_layout.addRow(
            "Tolerance",
        self.field39A,
        )

        financial_layout.addRow(
            "Available With",
        self.available_with,
        )

        financial_layout.addRow(
            "Available By",
        self.available_by,
        )

        self.financial_tab.setLayout(financial_layout)

        ###################################################
        # Shipment Tab
        ####################################################

        shipment_layout = QFormLayout()

        self.field43P = QComboBox()
        self.field43P.addItems([
            "ALLOWED",
            "NOT ALLOWED",
        ])

        self.field43T = QComboBox()
        self.field43T.addItems([
            "ALLOWED",
            "NOT ALLOWED",
        ])

        self.field44A = QLineEdit()

        self.field44B = QLineEdit()

        self.field44C = QDateEdit()
        self.field44C.setCalendarPopup(True)
        self.field44C.setDate(QDate.currentDate())

        self.field44E = QLineEdit()

        self.field44F = QLineEdit()

        shipment_layout.addRow(
            "Partial Shipment",
            self.field43P,
        )

        shipment_layout.addRow(
            "Transshipment",
            self.field43T,
        )

        shipment_layout.addRow(
            "Place of Receipt",
            self.field44A,
        )

        shipment_layout.addRow(
            "Final Destination",
            self.field44B,
        )

        shipment_layout.addRow(
            "Latest Shipment Date",
            self.field44C,
        )

        shipment_layout.addRow(
            "Port of Loading",
            self.field44E,
        )

        shipment_layout.addRow(
            "Port of Discharge",
            self.field44F,
        )

        self.shipment_tab.setLayout(shipment_layout)

        ####################################################
        # Documents Tab
        ####################################################

        documents_layout = QFormLayout()

        self.commercial_invoice = QComboBox()
        self.commercial_invoice.addItems([
            "Required",
            "Not Required",
        ])

        self.packing_list = QComboBox()
        self.packing_list.addItems([
            "Required",
            "Not Required",
        ])

        self.bill_of_lading = QComboBox()
        self.bill_of_lading.addItems([
            "Required",
            "Not Required",
        ])

        self.certificate_origin = QComboBox()
        self.certificate_origin.addItems([
            "Required",
            "Not Required",
        ])

        self.insurance_certificate = QComboBox()
        self.insurance_certificate.addItems([
            "Required",
            "Not Required",
        ])

        self.additional_documents = QTextEdit()

        documents_layout.addRow(
            "Commercial Invoice",
        self.commercial_invoice,
        )

        documents_layout.addRow(
            "Packing List",
        self.packing_list,
        )

        documents_layout.addRow(
            "Bill of Lading",
        self.bill_of_lading,
        )

        documents_layout.addRow(
            "Certificate of Origin",
        self.certificate_origin,
        )

        documents_layout.addRow(
            "Insurance Certificate",
        self.insurance_certificate,
        )

        documents_layout.addRow(
            "Additional Documents",
        self.additional_documents,
        )

        self.documents_tab.setLayout(documents_layout)

        ####################################################
        # Conditions Tab
        ####################################################

        conditions_layout = QFormLayout()

        self.goods_description = QTextEdit()

        self.additional_conditions = QTextEdit()

        self.presentation_period = QLineEdit()

        self.sender_receiver = QTextEdit()

        conditions_layout.addRow(
            "Goods Description",
            self.goods_description,
        )

        conditions_layout.addRow(
            "Additional Conditions",
            self.additional_conditions,
        )

        conditions_layout.addRow(
            "Presentation Period",
            self.presentation_period,
        )

    conditions_layout.addRow(
        "Sender to Receiver Information",
        self.sender_receiver,
    )

    self.conditions_tab.setLayout(conditions_layout)

    ####################################################
    # SWIFT Preview Tab
    ####################################################

    preview_layout = QVBoxLayout()

    preview_title = QLabel("Generated MT700 SWIFT Message")
    preview_title.setObjectName("sectionTitle")

    self.swift_preview = QTextEdit()

    self.swift_preview.setReadOnly(True)

    self.swift_preview.setPlaceholderText(
    """SWIFT MT700 Preview

    :20:
    LC Reference

    :31C:
    Issue Date

    :31D:
    Expiry Date

    :40A:
    Form of Documentary Credit

    :50:
    Applicant

    :59:
    Beneficiary

    :32B:
    Currency / Amount

    ...
    """
    )

    preview_layout.addWidget(preview_title)

    preview_layout.addWidget(self.swift_preview)

    self.preview_tab.setLayout(preview_layout)

    ####################################################
    # Action Buttons
    ####################################################

    button_layout = QHBoxLayout()

    self.save_button = QPushButton("💾 Save")

    self.load_button = QPushButton("📂 Load")

    self.swift_button = QPushButton("📡 Generate SWIFT")

    self.pdf_button = QPushButton("📄 Generate PDF")

    self.email_button = QPushButton("✉️ Send Email")

    button_layout.addWidget(self.save_button)

    button_layout.addWidget(self.load_button)

    button_layout.addStretch()

    button_layout.addWidget(self.swift_button)

    button_layout.addWidget(self.pdf_button)

    button_layout.addWidget(self.email_button)

    main_layout.addLayout(button_layout)

    ####################################################
    # Button Connections
    ####################################################

    self.save_button.clicked.connect(self.save_mt700)

    self.load_button.clicked.connect(self.load_mt700)

    self.swift_button.clicked.connect(self.generate_swift)

    self.pdf_button.clicked.connect(self.generate_pdf)

    self.email_button.clicked.connect(self.send_email)

    ####################################################
    # Save
    ####################################################

    def save_mt700(self):
        print("Save clicked")

    ####################################################
    # Load
    ####################################################

    def load_mt700(self):
        print("Load clicked")

    ####################################################
    # Generate SWIFT
    ####################################################

    def generate_swift(self):
        print("Generate SWIFT clicked")

    ####################################################
    # Generate PDF
    ####################################################

    def generate_pdf(self):
        print("Generate PDF clicked")

    ####################################################
    # Email
    ####################################################

    def send_email(self):
        print("Send Email clicked")

