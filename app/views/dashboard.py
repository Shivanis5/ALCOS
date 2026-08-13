from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)

from app.widgets.sidebar import Sidebar
from app.widgets.header import Header
from app.widgets.stat_card import StatCard
from app.widgets.recent_lc_table import RecentLCTable
from app.widgets.trade_summary import TradeSummary
from app.widgets.action_panel import ActionPanel
from app.views.transaction_workspace import TransactionWorkspace


class Dashboard(QWidget):
    """
    Main dashboard of ALCOS.
    """

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("ALCOS Dashboard")

        self.showMaximized()

        #####################################################
        # Main Layout
        #####################################################

        main_layout = QHBoxLayout(self)

        #####################################################
        # Sidebar
        #####################################################

        sidebar = Sidebar()

        main_layout.addWidget(sidebar)

        #####################################################
        # Right Side
        #####################################################

        right_layout = QVBoxLayout()

        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        #####################################################
        # Header
        #####################################################

        header = Header()

        right_layout.addWidget(header)

        #####################################################
        # Statistics Cards
        #####################################################

        cards_layout = QHBoxLayout()

        cards_layout.setSpacing(20)

        cards_layout.addWidget(
            StatCard(
                "Total LC",
                "125",
            )
        )

        cards_layout.addWidget(
            StatCard(
                "Pending",
                "18",
            )
        )

        cards_layout.addWidget(
            StatCard(
                "Approved",
                "97",
            )
        )

        cards_layout.addWidget(
            StatCard(
                "Rejected",
                "10",
            )
        )

        right_layout.addLayout(cards_layout)

        #####################################################
        # Quick Actions
        #####################################################

        self.action_panel = ActionPanel()

        self.action_panel.createTransactionRequested.connect(
          self.open_transaction_workspace
        )

        right_layout.addWidget(self.action_panel)

        #####################################################
        # Recent Letters of Credit
        #####################################################

        recent_table = RecentLCTable()

        right_layout.addWidget(recent_table)

        #####################################################
        # Welcome Message
        #####################################################

       # welcome = QLabel("Welcome to ALCOS Operating System")

        #welcome.setAlignment(Qt.AlignCenter)

        ##right_layout.addWidget(welcome)
        #####################################################
        # Trade Finance Operations
      #####################################################

        trade_summary = TradeSummary()

        right_layout.addWidget(trade_summary)

        #####################################################
        # Push everything to the top
        #####################################################

        right_layout.addStretch()

        #####################################################

        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
    #####################################################
    # Open Transaction Workspace
    ####################################################

    def open_transaction_workspace(self):

        self.transaction_workspace = TransactionWorkspace()

        self.transaction_workspace.show()
        