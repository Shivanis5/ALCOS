from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class RecentLCTable(QFrame):
    """
    Displays recently created Letters of Credit.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("recentLCTable")

        layout = QVBoxLayout(self)

        title = QLabel("Recent Letters of Credit")
        title.setObjectName("sectionTitle")

        table = QTableWidget()

        table.setColumnCount(4)

        table.setHorizontalHeaderLabels(
            [
                "LC Number",
                "Applicant",
                "Bank",
                "Status",
            ]
        )

        table.setRowCount(4)

        data = [
            ["LC001", "ABC Ltd", "SBI", "Approved"],
            ["LC002", "XYZ Pvt", "HDFC", "Pending"],
            ["LC003", "DEF Corp", "ICICI", "Rejected"],
            ["LC004", "PQR Ltd", "Axis", "Approved"],
        ]

        for row in range(len(data)):
            for col in range(len(data[row])):
                table.setItem(
                    row,
                    col,
                    QTableWidgetItem(data[row][col]),
                )

        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setDefaultSectionSize(150)

        layout.addWidget(title)
        layout.addWidget(table)
    