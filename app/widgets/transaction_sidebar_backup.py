from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
)


class TransactionSidebar(QWidget):
    """
    Navigation sidebar inside Trade Transaction Workspace.
    """

    moduleSelected = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("transactionSidebar")

        self.build_ui()

    def build_ui(self):

        self.setFixedWidth(220)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(15, 20, 15, 20)

        layout.setSpacing(12)


        modules = [
            ("📋 General Information", "general"),
            ("📄 MT700", "mt700"),
            ("✏️ MT707", "mt707"),
            ("📁 Documents", "documents"),
            ("🤖 OCR + AI", "ocr"),
            ("✔ Validation", "validation"),
            ("⚠ Risk", "risk"),
            ("🛡 Compliance", "compliance"),
            ("📑 PDF", "pdf"),
            ("📧 Email", "email"),
        ]


        for text, key in modules:

            button = QPushButton(text)

            button.setMinimumHeight(42)

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False, k=key:
                self.moduleSelected.emit(k)
            )

            layout.addWidget(button)


        layout.addStretch()