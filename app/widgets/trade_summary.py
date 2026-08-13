from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QGridLayout,
)


class TradeSummary(QFrame):
    """
    Trade Finance Operations summary panel.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("tradeSummary")

        self._build_ui()

    def _build_ui(self) -> None:

        layout = QGridLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)

        layout.setHorizontalSpacing(40)

        layout.setVerticalSpacing(12)

        title = QLabel("Trade Finance Operations")

        title.setObjectName("sectionTitle")

        layout.addWidget(title, 0, 0, 1, 2)

        rows = [

            ("Pending Review", "25"),

            ("Ready for Submission", "11"),

            ("High Risk Transactions", "4"),

            ("Rejected Yesterday", "2"),

            ("Compliance Score", "96%"),

        ]

        row = 1

        for label_text, value in rows:

            label = QLabel(label_text)

            value_label = QLabel(value)

            value_label.setObjectName("summaryValue")

            layout.addWidget(label, row, 0)

            layout.addWidget(value_label, row, 1)

            row += 1
            