from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QApplication

from app.core.database import DatabaseManager
from app.core.logger import LoggerManager
from app.core.theme import ThemeManager

from app.views.boot_screen import BootScreen
from app.views.login_screen import LoginScreen
from app.views.dashboard import Dashboard


class ALCOSApplication:
    """
    Central application manager for the ALCOS desktop application.

    Responsible for:

    - Logger initialization
    - Theme loading
    - Database initialization
    - Boot Screen
    - Login Screen
    - Dashboard
    """

    def __init__(self, app: QApplication) -> None:

        self.app = app

        self.logger: Optional[LoggerManager] = None
        self.theme_manager: Optional[ThemeManager] = None
        self.database_manager: Optional[DatabaseManager] = None

        self.boot_screen: Optional[BootScreen] = None
        self.login_screen: Optional[LoginScreen] = None
        self.dashboard: Optional[Dashboard] = None

    #################################################################
    # Application Startup
    #################################################################

    def start(self) -> None:

        self._initialize_logger()

        self._initialize_theme()

        db_ok = self._initialize_database()

        if db_ok:
            self.show_boot_screen()

    #################################################################
    # Logger
    #################################################################

    def _initialize_logger(self) -> None:

        self.logger = LoggerManager()

        self.logger.info("Starting ALCOS...")

    #################################################################
    # Theme
    #################################################################

    def _initialize_theme(self) -> None:

        self.theme_manager = ThemeManager()

        applied = self.theme_manager.apply_theme(self.app)

        if self.logger:

            if applied:
                self.logger.info("Theme loaded successfully")
            else:
                self.logger.warning("Theme could not be applied.")

    #################################################################
    # Database
    #################################################################

    def _initialize_database(self) -> bool:

        self.database_manager = DatabaseManager()

        try:

            self.database_manager.connect()

            if self.logger:
                self.logger.info("Database initialized successfully")

            return True

        except Exception:

            if self.logger:
                self.logger.exception("Database initialization failed")

            return False

    #################################################################
    # Boot Screen
    #################################################################

    def show_boot_screen(self) -> None:

        self.boot_screen = BootScreen()

        self.boot_screen.bootCompleted.connect(
            self.show_login_screen
        )

        self.boot_screen.show()

    #################################################################
    # Login Screen
    #################################################################

    def show_login_screen(self) -> None:

        if self.boot_screen:
            self.boot_screen.close()

        self.login_screen = LoginScreen()

        self.login_screen.loginSuccessful.connect(
            self.show_dashboard
        )

        self.login_screen.show()

    #################################################################
    # Dashboard
    #################################################################

    def show_dashboard(self, username: str) -> None:

        if self.login_screen:
            self.login_screen.close()

        self.dashboard = Dashboard()

        self.dashboard.show()

        if self.logger:
            self.logger.info(
                f"User '{username}' logged into ALCOS."
            )
