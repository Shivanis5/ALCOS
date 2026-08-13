from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
)

from app.widgets.modules.base_module import BaseModule


class MT707Widget(BaseModule):

    def __init__(self):
        super().__init__("MT707 - Amendment to Documentary Credit")

        layout = QVBoxLayout()

        ####################################################
        # Reference LC
        ####################################################

        layout.addWidget(QLabel("Reference LC Number"))

        self.reference_lc = QLineEdit()
        self.reference_lc.setPlaceholderText("LC2300285")

        layout.addWidget(self.reference_lc)

        self.load_button = QPushButton("Load Existing LC")

        layout.addWidget(self.load_button)

        ####################################################
        # Amendment Number
        ####################################################

        layout.addWidget(QLabel("Amendment Number"))

        self.amendment_no = QLineEdit()
        self.amendment_no.setPlaceholderText("001")

        layout.addWidget(self.amendment_no)

        ####################################################
        # Amendment Type
        ####################################################

        layout.addWidget(QLabel("Amendment Type"))

        self.amendment_type = QComboBox()

        self.amendment_type.addItems([
            "Increase Amount",
            "Reduce Amount",
            "Extend Expiry Date",
            "Shipment Date",
            "Goods Description",
            "Beneficiary Details",
            "Other"
        ])

        layout.addWidget(self.amendment_type)

        ####################################################
        # Current Value
        ####################################################

        layout.addWidget(QLabel("Current Value"))

        self.current_value = QLineEdit()

        layout.addWidget(self.current_value)

        ####################################################
        # New Value
        ####################################################

        layout.addWidget(QLabel("New Value"))

        self.new_value = QLineEdit()

        layout.addWidget(self.new_value)

        ####################################################
        # Reason
        ####################################################

        layout.addWidget(QLabel("Reason for Amendment"))

        self.reason = QTextEdit()

        layout.addWidget(self.reason)

        ####################################################
        # Buttons
        ####################################################

        buttons = QHBoxLayout()

        self.save_button = QPushButton("Save Amendment")

        self.swift_button = QPushButton("Generate MT707")

        self.pdf_button = QPushButton("Generate Amendment PDF")

        self.email_button = QPushButton("Email Amendment")

        buttons.addWidget(self.save_button)
        buttons.addWidget(self.swift_button)
        buttons.addWidget(self.pdf_button)
        buttons.addWidget(self.email_button)

        layout.addLayout(buttons)

        layout.addStretch()

        self.main_layout.addLayout(layout)