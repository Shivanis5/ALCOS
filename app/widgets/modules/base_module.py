from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)


class BaseModule(QWidget):
    """
    Base class for all ALCOS transaction modules.
    """

    def __init__(self, title: str):
        super().__init__()

        self.main_layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")

        self.main_layout.addWidget(title_label)