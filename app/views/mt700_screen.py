from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QScrollArea,
)


class MT700Screen(QWidget):
    """
    MT700 Letter of Credit Issuance Screen.
    """

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def create_section(self, title: str) -> QFrame:

        frame = QFrame()

        frame.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(frame)

        label = QLabel(title)

        label.setStyleSheet(
            "font-size:18px;"
            "font-weight:bold;"
        )

        layout.addWidget(label)

        layout.addStretch()

        return frame

    def setup_ui(self):

        self.setWindowTitle("MT700 - Issue Letter of Credit")

        self.showMaximized()

        main_layout = QVBoxLayout(self)

        title = QLabel("Issue Letter of Credit (MT700)")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(
            "font-size:26px;"
            "font-weight:bold;"
        )

        main_layout.addWidget(title)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QWidget()

        container_layout = QVBoxLayout(container)

        sections = [

            "General Information",

            "Applicant Details",

            "Beneficiary Details",

            "Issuing Bank",

            "Advising Bank",

            "Shipment Details",

            "Goods Description",

            "Required Documents",

            "Additional Conditions",

        ]

        for section in sections:

            container_layout.addWidget(
                self.create_section(section)
            )

        button = QPushButton(
            "Generate MT700"
        )

        button.setMinimumHeight(50)

        container_layout.addWidget(button)

        scroll.setWidget(container)

        main_layout.addWidget(scroll)
