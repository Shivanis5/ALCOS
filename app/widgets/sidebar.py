from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Sidebar(QWidget):
    """
    Left navigation sidebar for ALCOS.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("sidebar")

        self._build_ui()

    def _build_ui(self) -> None:

        self.setFixedWidth(220)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(15, 20, 15, 20)

        layout.setSpacing(12)

        buttons = [
            "🏠 Dashboard",
            "📄 MT700",
            "✏️ MT707",
            "📩 Messages",
            "📊 Reports",
            "👥 Users",
            "⚙️ Settings",
            "🚪 Logout",
        ]

        for text in buttons:

            button = QPushButton(text)

            button.setMinimumHeight(45)

            button.setCursor(Qt.PointingHandCursor)

            layout.addWidget(button)

        layout.addStretch()
    