from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGraphicsOpacityEffect,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.config import APP_NAME, APP_VERSION, IMAGES_DIR
from app.services.auth_service import (
    AuthError,
    AuthService,
)

_FADE_IN_DURATION_MS: int = 700
_PANEL_WIDTH: int = 480


class LoginScreen(QWidget):
    """Professional banking-style login screen for ALCOS.

    Displays credential fields and emits ``loginSuccessful`` carrying the
    entered credentials. Authentication is performed by the application
    controller; failures are reported back through ``show_auth_error``.

    When no local user account exists yet, the screen switches to an
    explicit ``Create Initial Administrator`` bootstrap mode so the
    application can never lock itself out on first launch.

    The login screen opens frameless in full-screen mode with a centered
    login panel to resemble a real operating-system sign-in experience.
    """

    loginSuccessful = Signal(str, str)

    def __init__(
        self,
        auth_service: AuthService | None = None,
    ) -> None:
        """Initialize the login screen and build its user interface."""
        super().__init__()

        self.auth_service = auth_service or AuthService()

        self._bootstrap_mode: bool = not (
            self.auth_service.has_any_user()
        )

        self.logo_label = QLabel()
        self.title_label = QLabel(APP_NAME)
        self.subtitle_label = QLabel(
            "Automated Letter of Credit Operating System"
        )
        self.heading_label = QLabel("User Login")

        self.username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.confirm_password_label = QLabel("Confirm Password")
        self.confirm_password_input = QLineEdit()
        self.remember_checkbox = QCheckBox("Remember Me")
        self.login_button = QPushButton("Login")
        self.footer_label = QLabel(
            f"Version {APP_VERSION}\n© 2026 ALCOS Financial Systems"
        )

        self._opacity_effect: QGraphicsOpacityEffect | None = None
        self._fade_animation: QPropertyAnimation | None = None

        self._setup_ui()
        self._load_logo()
        self._connect_signals()
        self._apply_mode()

    def _setup_ui(self) -> None:
        """Build and configure the login screen user interface."""
        self.setWindowTitle(f"{APP_NAME} | User Login")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_panel = QFrame()
        login_panel.setObjectName("loginPanel")
        login_panel.setFixedWidth(_PANEL_WIDTH)

        panel_layout = QVBoxLayout(login_panel)
        panel_layout.setContentsMargins(40, 40, 40, 32)
        panel_layout.setSpacing(12)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(96)

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("loginTitle")

        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setObjectName("loginSubtitle")

        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading_label.setObjectName("loginHeading")

        self.username_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setObjectName("usernameInput")
        self._configure_input_field(self.username_input)

        self.password_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setObjectName("passwordInput")
        self._configure_input_field(self.password_input)

        self.confirm_password_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.confirm_password_input.setPlaceholderText(
            "Repeat Password"
        )
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setObjectName("confirmPasswordInput")
        self._configure_input_field(self.confirm_password_input)

        self.remember_checkbox.setObjectName("rememberCheckbox")

        self.login_button.setObjectName("loginButton")
        self.login_button.setMinimumHeight(50)
        self.login_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setObjectName("footerLabel")

        panel_layout.addWidget(
            self.logo_label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        panel_layout.addWidget(self.title_label)
        panel_layout.addWidget(self.subtitle_label)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(self.heading_label)
        panel_layout.addSpacing(16)
        panel_layout.addWidget(self.username_label)
        panel_layout.addWidget(self.username_input)
        panel_layout.addWidget(self.password_label)
        panel_layout.addWidget(self.password_input)
        panel_layout.addWidget(self.confirm_password_label)
        panel_layout.addWidget(self.confirm_password_input)
        panel_layout.addWidget(self.remember_checkbox)
        panel_layout.addSpacing(8)
        panel_layout.addWidget(self.login_button)
        panel_layout.addSpacing(16)
        panel_layout.addWidget(self.footer_label)

        main_layout.addStretch(1)
        main_layout.addWidget(
            login_panel,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        main_layout.addStretch(1)

        self.setLayout(main_layout)

        QWidget.setTabOrder(self.username_input, self.password_input)
        QWidget.setTabOrder(
            self.password_input, self.confirm_password_input
        )
        QWidget.setTabOrder(
            self.confirm_password_input, self.remember_checkbox
        )
        QWidget.setTabOrder(self.remember_checkbox, self.login_button)

    def _configure_input_field(self, field: QLineEdit) -> None:
        """Apply consistent sizing to credential input fields.

        Args:
            field: The line edit to configure.
        """
        field.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        field.setMinimumHeight(40)

    def show(self) -> None:
        """Display the login screen in full-screen mode with a fade-in effect."""
        super().showFullScreen()
        self.raise_()
        self.activateWindow()
        self.username_input.setFocus()
        self._play_fade_in()

    def _play_fade_in(self) -> None:
        """Play a one-time fade-in animation when the login screen appears."""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_animation = QPropertyAnimation(
            self._opacity_effect,
            b"opacity",
            self,
        )
        self._fade_animation.setDuration(_FADE_IN_DURATION_MS)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(1.0)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.start()

    def _connect_signals(self) -> None:
        """Connect UI signals to login screen handlers."""
        self.login_button.clicked.connect(self._on_submit)
        self.username_input.returnPressed.connect(self._on_submit)
        self.password_input.returnPressed.connect(self._on_submit)
        self.confirm_password_input.returnPressed.connect(
            self._on_submit
        )

    #################################################################
    # Bootstrap / login mode handling
    #################################################################

    def _apply_mode(self) -> None:
        """Show bootstrap or normal-login controls for current mode."""
        is_bootstrap = self._bootstrap_mode

        self.heading_label.setText(
            "Create Initial Administrator"
            if is_bootstrap
            else "User Login"
        )

        self.login_button.setText(
            "Create Initial Administrator"
            if is_bootstrap
            else "Login"
        )

        self.confirm_password_label.setVisible(is_bootstrap)
        self.confirm_password_input.setVisible(is_bootstrap)
        self.remember_checkbox.setVisible(not is_bootstrap)

    def _on_submit(self) -> None:
        """Dispatch submit according to the active mode."""
        if self._bootstrap_mode:
            self._attempt_bootstrap()
        else:
            self._attempt_login()

    def _load_logo(self) -> None:
        """Load the company logo when available.

        If ``resources/images/logo.png`` does not exist or cannot be loaded,
        the logo label is hidden gracefully.
        """
        logo_path = Path(IMAGES_DIR) / "logo.png"
        if not logo_path.is_file():
            self.logo_label.hide()
            return

        pixmap = QPixmap(str(logo_path))
        if pixmap.isNull():
            self.logo_label.hide()
            return

        scaled_logo = pixmap.scaled(
            140,
            140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.show()

    def _attempt_login(self) -> None:
        """Validate input and emit ``loginSuccessful`` when credentials are present."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            QMessageBox.warning(
                self,
                "Login Required",
                "Please enter your username.",
            )
            self.username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(
                self,
                "Login Required",
                "Please enter your password.",
            )
            self.password_input.setFocus()
            return

        self.loginSuccessful.emit(username, password)

    def _attempt_bootstrap(self) -> None:
        """Create the initial administrator, then switch to login mode."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirmation = self.confirm_password_input.text()

        try:
            self.auth_service.create_initial_admin(
                username,
                password,
                confirmation,
            )

        except AuthError as exc:
            QMessageBox.warning(
                self,
                "Administrator Setup",
                str(exc),
            )
            return

        except Exception:
            self.auth_service.logger.exception(
                "Unexpected failure during administrator bootstrap."
            )
            QMessageBox.critical(
                self,
                "Administrator Setup",
                "The administrator account could not be created. "
                "Please try again.",
            )
            return

        self.password_input.clear()
        self.confirm_password_input.clear()

        self._bootstrap_mode = False
        self._apply_mode()

        self.username_input.setFocus()

        QMessageBox.information(
            self,
            "Administrator Created",
            f"Administrator '{username}' was created.\n\n"
            "Please sign in with your new credentials.",
        )

    def show_auth_error(self, message: str) -> None:
        """Display an authentication failure reported by the controller."""
        self.password_input.clear()
        self.password_input.setFocus()

        QMessageBox.warning(
            self,
            "Login Failed",
            message,
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard shortcuts for the login screen.

        Args:
            event: The key press event.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)
