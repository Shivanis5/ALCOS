"""
ALCOS Application Logging
=========================

Provides a singleton logger manager that configures application-wide
logging to both the console and a rotating log file.

This module depends only on Python's built-in ``logging`` package and
reads paths and feature flags from ``app.core.config``. It contains no
GUI code, database access, email transport, or business logic.

Typical usage::

    from app.core.logger import LoggerManager

    logger = LoggerManager()
    logger.info("Theme loaded successfully")
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import APP_NAME, ENABLE_LOGGING, LOG_PATH

# Maximum size of a single log file before rotation (5 MB).
_MAX_BYTES: int = 5 * 1024 * 1024

# Number of rotated backup files to retain.
_BACKUP_COUNT: int = 5

# Shared log record format: timestamp | level | app name | message
_LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class LoggerManager:
    """
    Singleton manager for ALCOS application logging.

    Configures a named logger that writes to the console and, when
    ``ENABLE_LOGGING`` is ``True``, to a rotating UTF-8 log file at
    ``LOG_PATH``. When file logging is disabled the application continues
    normally with console-only output (or a silent NullHandler fallback
    if no handlers remain usable).

    Attributes:
        _instance: The sole ``LoggerManager`` instance.
        _logger: The underlying ``logging.Logger`` used by convenience
            methods.
        _configured: Whether handlers have already been attached.
    """

    _instance: Optional[LoggerManager] = None
    _logger: logging.Logger
    _configured: bool

    def __new__(cls) -> LoggerManager:
        """
        Return the singleton instance, creating it on first construction.

        Returns:
            The shared ``LoggerManager`` instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._configured = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the logger on first construction only.

        Subsequent instantiations are no-ops because ``__new__`` always
        returns the existing singleton.
        """
        if self._configured:
            return
        self._configure()
        self._configured = True

    def _configure(self) -> None:
        """
        Attach console and optional rotating-file handlers to the logger.

        Ensures the log directory exists before creating the file handler.
        File-handler failures are reported to stderr without raising so the
        application can continue running.
        """
        self._logger = logging.getLogger(APP_NAME)
        self._logger.setLevel(logging.DEBUG)
        # Avoid duplicate handlers if configuration is invoked more than once.
        self._logger.handlers.clear()
        self._logger.propagate = False

        formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        if not ENABLE_LOGGING:
            return

        try:
            log_path = Path(LOG_PATH)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                filename=str(log_path),
                maxBytes=_MAX_BYTES,
                backupCount=_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except OSError as exc:
            print(
                f"[ALCOS Logger] Warning: Failed to configure file logging "
                f"at '{LOG_PATH}': {exc}. Console logging remains active.",
                file=sys.stderr,
            )

    def get_logger(self) -> logging.Logger:
        """
        Return the underlying configured ``logging.Logger`` instance.

        Returns:
            The application logger named after ``APP_NAME``.
        """
        return self._logger

    def debug(self, message: str) -> None:
        """
        Log a debug-level message.

        Args:
            message: The message text to record.
        """
        self._logger.debug(message)

    def info(self, message: str) -> None:
        """
        Log an informational message.

        Args:
            message: The message text to record.
        """
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """
        Log a warning-level message.

        Args:
            message: The message text to record.
        """
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """
        Log an error-level message.

        Args:
            message: The message text to record.
        """
        self._logger.error(message)

    def critical(self, message: str) -> None:
        """
        Log a critical-level message.

        Args:
            message: The message text to record.
        """
        self._logger.critical(message)

    def exception(self, message: str) -> None:
        """
        Log an exception with traceback.

        Args:
            message: Message describing the exception.
        """
        self._logger.exception(message)
