"""
ALCOS Application Configuration
===============================

Central configuration module for the Automated Letter of Credit Operating
System (ALCOS). All application-wide constants, filesystem paths, and
feature flags are defined here and should be imported by other modules
rather than duplicated elsewhere.

This module is deliberately free of GUI code, database drivers, email
transport, business logic, and PySide widget dependencies. It only
defines configuration values and ensures required directories exist on
import.

Typical usage::

    from app.core.config import (
        APP_NAME,
        DATABASE_PATH,
        LOG_PATH,
        STYLES_DIR,
    )

Directory layout resolved from this module::

    PROJECT_ROOT/
    ├── app/
    ├── config/
    ├── database/
    ├── generated/
    │   ├── mt700/
    │   ├── mt707/
    │   └── pdf/
    ├── logs/
    └── resources/
        ├── fonts/
        ├── icons/
        ├── images/
        └── styles/
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Application Metadata
# ---------------------------------------------------------------------------

APP_NAME: str = "ALCOS"
APP_VERSION: str = "1.0.0"
COMPANY_NAME: str = "ALCOS Financial Systems"
ORGANIZATION_NAME: str = "ALCOS"

# ---------------------------------------------------------------------------
# Window Configuration
# ---------------------------------------------------------------------------

WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 800
WINDOW_MIN_WIDTH: int = 1024
WINDOW_MIN_HEIGHT: int = 768

# ---------------------------------------------------------------------------
# Boot Configuration
# ---------------------------------------------------------------------------

BOOT_DURATION_MS: int = 3000

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

DEFAULT_THEME: str = "default"
STYLESHEET_FILENAME: str = "theme.qss"

# ---------------------------------------------------------------------------
# Filesystem Paths
# ---------------------------------------------------------------------------

# config.py lives at app/core/config.py; project root is three levels up.
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent

APP_DIR: Path = PROJECT_ROOT / "app"
RESOURCES_DIR: Path = PROJECT_ROOT / "resources"
DATABASE_DIR: Path = PROJECT_ROOT / "database"
GENERATED_DIR: Path = PROJECT_ROOT / "generated"
LOGS_DIR: Path = PROJECT_ROOT / "logs"

IMAGES_DIR: Path = RESOURCES_DIR / "images"
ICONS_DIR: Path = RESOURCES_DIR / "icons"
FONTS_DIR: Path = RESOURCES_DIR / "fonts"
STYLES_DIR: Path = RESOURCES_DIR / "styles"

PDF_OUTPUT_DIR: Path = GENERATED_DIR / "pdf"
MT700_OUTPUT_DIR: Path = GENERATED_DIR / "mt700"
MT707_OUTPUT_DIR: Path = GENERATED_DIR / "mt707"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASE_FILENAME: str = "alcos.db"
DATABASE_PATH: Path = DATABASE_DIR / DATABASE_FILENAME

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_FILENAME: str = "alcos.log"
LOG_PATH: Path = LOGS_DIR / LOG_FILENAME

# ---------------------------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------------------------

ENABLE_DATABASE: bool = True
ENABLE_LOGGING: bool = True
ENABLE_EMAIL: bool = False
ENABLE_PDF: bool = True
ENABLE_BOOT_ANIMATION: bool = True

# ---------------------------------------------------------------------------
# Directory Initialization
# ---------------------------------------------------------------------------

_REQUIRED_DIRECTORIES: tuple[Path, ...] = (
    DATABASE_DIR,
    GENERATED_DIR,
    LOGS_DIR,
    IMAGES_DIR,
    ICONS_DIR,
    FONTS_DIR,
    STYLES_DIR,
    PDF_OUTPUT_DIR,
    MT700_OUTPUT_DIR,
    MT707_OUTPUT_DIR,
)


def _ensure_directories() -> None:
    """
    Create all required project directories if they do not already exist.

    Called once at module import time so downstream modules can rely on
    paths being writable without performing their own bootstrapping.
    """
    for directory in _REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


_ensure_directories()
