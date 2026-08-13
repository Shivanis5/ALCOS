from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.core.config import APP_NAME, APP_VERSION, BOOT_DURATION_MS, IMAGES_DIR

_FADE_IN_DURATION_MS: int = 800


class BootScreen(QWidget):
    """Animated startup screen displayed when ALCOS launches.

    The screen shows branding, a progress bar, and rotating status messages
    while the application performs startup work. When the animation reaches
    100 percent, the screen emits ``bootCompleted``.

    The boot screen opens frameless in full-screen mode to resemble a real
    operating-system startup sequence.
    """

    bootCompleted = Signal()

    def __init__(self) -> None:
        """Initialize the boot screen and start the progress animation."""
        super().__init__()

        self._status_messages: list[str] = [
            "Starting ALCOS...",
            "Loading Configuration...",
            "Loading Theme...",
            "Connecting Database...",
            "Loading Banking Services...",
            "Preparing User Interface...",
            "Welcome to ALCOS",
        ]
        self._progress_value: int = 0
        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)

        self.logo_label = QLabel()
        self.title_label = QLabel(APP_NAME)
        self.subtitle_label = QLabel(
            "Automated Letter of Credit Operating System"
        )
        self.status_label = QLabel(self._status_messages[0])
        self.progress_bar = QProgressBar()
        self.version_label = QLabel(f"Version {APP_VERSION}")

        self._opacity_effect: QGraphicsOpacityEffect | None = None
        self._fade_animation: QPropertyAnimation | None = None

        self._setup_ui()
        self._load_logo()
        self._start_animation()

    def _setup_ui(self) -> None:
        """Build and configure the boot screen user interface."""
        self.setWindowTitle(f"{APP_NAME} | Operating System Startup")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(96)

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("bootTitleLabel")

        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setObjectName("bootSubtitleLabel")

        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("bootStatusLabel")

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumWidth(320)
        self.progress_bar.setMaximumWidth(520)
        self.progress_bar.setObjectName("bootProgressBar")

        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setObjectName("bootVersionLabel")

        layout.addStretch(1)
        layout.addWidget(self.logo_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addSpacing(8)
        layout.addWidget(self.status_label)
        layout.addWidget(
            self.progress_bar,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addSpacing(8)
        layout.addWidget(self.version_label)
        layout.addStretch(1)

        self.setLayout(layout)

    def show(self) -> None:
        """Display the boot screen in full-screen mode with a fade-in effect."""
        super().showFullScreen()
        self.raise_()
        self.activateWindow()
        self._play_fade_in()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard input for the boot screen.

        Args:
            event: The key press event.
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def _play_fade_in(self) -> None:
        """Play a one-time fade-in animation when the boot screen appears."""
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

    def _load_logo(self) -> None:
        """Load the company logo when available.

        If ``resources/images/logo.png`` does not exist or cannot be loaded,
        the screen falls back to showing only the application title.
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
            180,
            180,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_label.setPixmap(scaled_logo)
        self.logo_label.show()

    def _start_animation(self) -> None:
        """Start the timer-driven boot progress animation."""
        interval_ms = max(1, BOOT_DURATION_MS // 100)
        self._timer.start(interval_ms)

    def _update_progress(self) -> None:
        """Advance the progress bar and rotate startup status messages."""
        self._progress_value = min(self._progress_value + 1, 100)
        self.progress_bar.setValue(self._progress_value)
        self._update_status_message()

        if self._progress_value >= 100:
            self._timer.stop()
            self.hide()
            self.bootCompleted.emit()

    def _update_status_message(self) -> None:
        """Update the status label based on the current progress."""
        message_count = len(self._status_messages)
        if message_count == 0:
            return

        index = min(
            (self._progress_value * message_count) // 100,
            message_count - 1,
        )
        self.status_label.setText(self._status_messages[index])
