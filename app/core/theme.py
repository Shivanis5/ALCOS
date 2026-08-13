"""
ALCOS Theme Management
======================

Provides utilities for loading and applying the application-wide Qt Style
Sheet (QSS) theme. This module depends on PySide6 for ``QApplication`` and
reads stylesheet paths from ``app.core.config``.

This module intentionally contains no widgets, views, or business logic.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.core.config import STYLESHEET_FILENAME, STYLES_DIR


class ThemeManager:
    """
    Loads and applies the ALCOS QSS theme to a ``QApplication`` instance.

    The stylesheet path is resolved from configuration constants:
    ``STYLES_DIR / STYLESHEET_FILENAME``.
    """

    def __init__(self) -> None:
        """Initialize the theme manager with the configured stylesheet path."""
        self._stylesheet_path: Path = STYLES_DIR / STYLESHEET_FILENAME

    def apply_theme(self, app: QApplication) -> bool:
        """
        Load the QSS theme file and apply it to the given application.

        If the stylesheet file exists, it is read as UTF-8 and applied via
        ``QApplication.setStyleSheet()``. Missing files and read failures
        are reported without raising exceptions so the application can
        continue with default Qt styling.

        Args:
            app: The active Qt application instance to style.

        Returns:
            ``True`` if the stylesheet was loaded and applied successfully;
            ``False`` if the file is missing or could not be read.
        """
        if not self._stylesheet_path.is_file():
            print(
                f"[ALCOS Theme] Warning: Stylesheet not found at "
                f"'{self._stylesheet_path}'. Using default Qt styling."
            )
            return False

        try:
            stylesheet = self._stylesheet_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(
                f"[ALCOS Theme] Warning: Failed to read stylesheet at "
                f"'{self._stylesheet_path}': {exc}. Using default Qt styling."
            )
            return False
        except UnicodeDecodeError as exc:
            print(
                f"[ALCOS Theme] Warning: Stylesheet at "
                f"'{self._stylesheet_path}' is not valid UTF-8: {exc}. "
                f"Using default Qt styling."
            )
            return False

        app.setStyleSheet(stylesheet)
        return True
