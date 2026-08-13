from __future__ import annotations

from PySide6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.widgets.modules.base_module import BaseModule
from PySide6.QtWidgets import QMessageBox
from app.services.email_service import EmailService


class EmailWidget(BaseModule):

    def __init__(self):
        super().__init__("Email Module")

        self.email_service = EmailService()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Receiver Email"))

        self.receiver = QLineEdit()
        self.receiver.setPlaceholderText("customer@example.com")

        layout.addWidget(self.receiver)

        ###################################################
        # Subject
        ###################################################

        layout.addWidget(QLabel("Subject"))

        self.subject = QLineEdit()
        self.subject.setText("LC MT700")

        layout.addWidget(self.subject)

        self.send_button = QPushButton("Send Email")

        self.send_button.clicked.connect(
            self.send_email
        )

        layout.addWidget(self.send_button)

        layout.addStretch()

        self.main_layout.addLayout(layout)

    ###################################################
    # Send Email
    ###################################################

    def send_email(self):

        receiver = self.receiver.text().strip()

        if not receiver:

            QMessageBox.warning(
                self,
                "Missing Email",
                "Please enter receiver email."
            )

            return

        subject = self.subject.text()

        body = (
            "Dear Customer,\n\n"
            "Please find attached the Letter of Credit.\n\n"
            "Regards,\n"
            "ALCOS Banking System"
        )

        from pathlib import Path

        pdf_folder = Path("generated/pdf")

        pdf_files = sorted(
            pdf_folder.glob("*_MT700.pdf"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        if not pdf_files:
            QMessageBox.warning(
                self,
                "No PDF Found",
                "Please generate an MT700 PDF first."
            )
            return

        attachment = str(pdf_files[0])

        self.email_service.send_email(
            receiver,
            subject,
            body,
            attachment
        )

        QMessageBox.information(
            self,
            "Success",
            "Email sent successfully."
        )