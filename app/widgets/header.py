from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
)


class Header(QWidget):
    """
    Top header displayed in the dashboard.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("header")

        self._build_ui()

    def _build_ui(self) -> None:

        self.setFixedHeight(70)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(20, 10, 20, 10)

        title = QLabel("ALCOS Dashboard")

        title.setObjectName("headerTitle")

        layout.addWidget(title)

        layout.addStretch()

        notification_button = QPushButton("🔔")

        profile_button = QPushButton("👤 Admin")

        layout.addWidget(notification_button)

        layout.addWidget(profile_button)
    