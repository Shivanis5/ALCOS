from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout,
)


class StatCard(QFrame):
    """
    Professional dashboard statistics card.
    """

    def __init__(self, title: str, value: str) -> None:
        super().__init__()

        self.setObjectName("statCard")

        self.setFixedSize(230, 140)

        self._build_ui(title, value)

    def _build_ui(self, title: str, value: str) -> None:

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20,
            15,
            20,
            15,
        )

        layout.setSpacing(8)

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setObjectName(
            "statTitle"
        )


        value_label = QLabel(value)

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        value_label.setObjectName(
            "statValue"
        )


        layout.addStretch()

        layout.addWidget(title_label)

        layout.addWidget(value_label)

        layout.addStretch()
    