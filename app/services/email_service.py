from __future__ import annotations

import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


class EmailService:

    def __init__(self):

        self.sender = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")

    def send_email(self, receiver, subject, body, attachment_path):

        msg = EmailMessage()

        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = receiver

        msg.set_content(body)

        with open(attachment_path, "rb") as file:

            msg.add_attachment(
                file.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(attachment_path),
            )

        try:

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:

                smtp.starttls()

                smtp.login(
                    self.sender,
                    self.password,
                )

                smtp.send_message(msg)

                print("✅ Email sent successfully!")

        except Exception as e:

            print("❌ EMAIL ERROR:", e)
        