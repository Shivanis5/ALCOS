from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)


class TransactionHeader(QWidget):
    """
    Header for individual trade transaction.
    """

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "transactionHeader"
        )

        self.build_ui()


    def build_ui(self):

        self.setFixedHeight(70)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            20,
            10,
            20,
            10
        )


        title = QLabel(
            "ALCOS Trade Transaction"
        )

        title.setObjectName(
            "headerTitle"
        )


        status = QLabel(
            "Status : Draft"
        )

        status.setObjectName(
            "statusLabel"
        )


        layout.addWidget(title)

        layout.addStretch()

        layout.addWidget(status)