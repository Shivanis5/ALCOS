from __future__ import annotations

from PySide6.QtCore import Qt, Signal

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
)


class ActionPanel(QFrame):
    """
    Quick Actions panel for ALCOS Dashboard.
    """

    createTransactionRequested = Signal()


    def __init__(self):

        super().__init__()

        self.setObjectName("actionPanel")

        self.setup_ui()


    def setup_ui(self):

        outer = QVBoxLayout(self)

        outer.setContentsMargins(
            20,
            20,
            20,
            20
        )

        outer.setSpacing(15)


        title = QLabel(
            "Quick Actions"
        )

        title.setObjectName(
            "sectionTitle"
        )

        outer.addWidget(title)


        grid = QGridLayout()

        grid.setHorizontalSpacing(20)

        grid.setVerticalSpacing(20)


        actions = [

            ("➕", "Create Trade\nTransaction"),

            ("📄", "Generate PDF"),

            ("📧", "Send Email\nNotification"),

            ("📥", "Import MT700"),

        ]


        for index, (icon, text) in enumerate(actions):

            button = QPushButton(
                f"{icon}\n\n{text}"
            )

            button.setMinimumSize(
                180,
                110
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.setObjectName(
                "actionButton"
            )


            # Connect only first button
            if index == 0:

                button.clicked.connect(
                    self.createTransactionRequested.emit
                )


            grid.addWidget(
                button,
                0,
                index
            )


        outer.addLayout(grid)