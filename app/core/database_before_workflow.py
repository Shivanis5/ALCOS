"""
ALCOS Database Management
=========================

Provides a singleton SQLite database manager for the Automated Letter of
Credit Operating System. Connections, schema creation, and parameterized
query helpers are centralized here.

This module contains no GUI code, email transport, or business logic. It
depends on ``sqlite3``, ``app.core.config``, and ``app.core.logger``.

Typical usage::

    from app.core.database import DatabaseManager

    db = DatabaseManager()
    db.connect()
    rows = db.fetchall("SELECT * FROM users WHERE role = ?", ("admin",))
    db.disconnect()
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

from app.core.config import DATABASE_PATH, ENABLE_DATABASE
from app.core.logger import LoggerManager

# SQL statements used to create the core schema on first launch.
_SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        created_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS letters_of_credit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lc_number TEXT UNIQUE,
        applicant TEXT,
        beneficiary TEXT,
        amount REAL,
        currency TEXT,
        status TEXT,
        issue_date TEXT,
        expiry_date TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS amendments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lc_number TEXT,
        field_changed TEXT,
        old_value TEXT,
        new_value TEXT,
        amended_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mt700 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lc_number TEXT UNIQUE,

    field_27 TEXT,
    field_40A TEXT,
    field_20 TEXT,
    field_23 TEXT,
    field_31C TEXT,
    field_31D TEXT,

    field_50 TEXT,
    field_59 TEXT,

    field_32B TEXT,

    field_39A TEXT,

    field_41A TEXT,

    field_42A TEXT,

    field_42C TEXT,

    field_43P TEXT,
    field_43T TEXT,

    field_44A TEXT,
    field_44B TEXT,
    field_44C TEXT,
    field_44D TEXT,
    field_44E TEXT,
    field_44F TEXT,

    field_44G TEXT,

    field_45A TEXT,

    field_46A TEXT,

    field_47A TEXT,

    field_71B TEXT,

    field_48 TEXT,

    field_49 TEXT,

    field_53A TEXT,

    field_57A TEXT,

    field_78 TEXT,

    field_72 TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        is_read INTEGER,
        created_at TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TEXT
    )
    """,
)


class DatabaseManager:
    """
    Singleton manager for the ALCOS SQLite database.

    Opens a connection to ``DATABASE_PATH``, enables foreign-key
    enforcement, and ensures the core schema exists. When
    ``ENABLE_DATABASE`` is ``False``, connection attempts are skipped and
    query helpers raise ``RuntimeError`` rather than silently corrupting
    application state.

    Attributes:
        _instance: The sole ``DatabaseManager`` instance.
        _connection: Active ``sqlite3.Connection``, or ``None``.
        _logger: Shared application logger.
        _initialized: Whether singleton state has been set up.
    """

    _instance: Optional[DatabaseManager] = None
    _connection: Optional[sqlite3.Connection]
    _logger: LoggerManager
    _initialized: bool

    def __new__(cls) -> DatabaseManager:
        """
        Return the singleton instance, creating it on first construction.

        Returns:
            The shared ``DatabaseManager`` instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize logger and connection state on first construction only.

        Subsequent instantiations are no-ops because ``__new__`` always
        returns the existing singleton.
        """
        if self._initialized:
            return
        self._logger = LoggerManager()
        self._connection = None
        self._initialized = True

    def connect(self) -> sqlite3.Connection:
        """
        Open the SQLite database connection and prepare the schema.

        Creates the database file and parent directory if needed, enables
        foreign keys, and runs ``create_tables()`` on first connect.
        When ``ENABLE_DATABASE`` is ``False``, no connection is opened.

        Returns:
            The active ``sqlite3.Connection``.

        Raises:
            RuntimeError: If database support is disabled via configuration.
            sqlite3.Error: If the connection or schema setup fails.
        """
        if not ENABLE_DATABASE:
            self._logger.warning(
                "Database support is disabled (ENABLE_DATABASE=False)."
            )
            raise RuntimeError("Database support is disabled.")

        if self._connection is not None:
            return self._connection

        try:
            db_path = Path(DATABASE_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            self._connection = sqlite3.connect(str(db_path))
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
            self._logger.info(f"Connected to database at '{db_path}'.")
            return self._connection
        except sqlite3.Error:
            self._logger.exception(
                f"Failed to connect to database at '{DATABASE_PATH}'."
            )
            self._connection = None
            raise

    def disconnect(self) -> None:
        """
        Close the SQLite connection safely.

        Commits any pending transaction before closing. No-op when no
        connection is open.
        """
        if self._connection is None:
            return

        try:
            self._connection.commit()
            self._connection.close()
            self._logger.info("Database connection closed.")
        except sqlite3.Error:
            self._logger.exception("Failed to close database connection.")
            raise
        finally:
            self._connection = None

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Return the active SQLite connection, connecting if necessary.

        Returns:
            The active ``sqlite3.Connection``.

        Raises:
            RuntimeError: If database support is disabled.
            sqlite3.Error: If a new connection cannot be established.
        """
        if self._connection is None:
            return self.connect()
        return self._connection

    def execute(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> sqlite3.Cursor:
        """
        Execute a single parameterized SQL statement.

        Args:
            query: SQL statement with ``?`` placeholders.
            parameters: Values bound to the placeholders.

        Returns:
            The ``sqlite3.Cursor`` produced by the statement.

        Raises:
            sqlite3.Error: If execution fails.
        """
        try:
            cursor = self.connection.execute(query, parameters)
            self._logger.debug(f"Executed SQL: {query.strip()}")
            return cursor
        except sqlite3.Error:
            self._logger.exception(f"SQL execute failed: {query.strip()}")
            self.rollback()
            raise

    def executemany(
        self,
        query: str,
        sequence: Sequence[Sequence[Any]],
    ) -> sqlite3.Cursor:
        """
        Execute a parameterized SQL statement against a sequence of rows.

        Args:
            query: SQL statement with ``?`` placeholders.
            sequence: Iterable of parameter sequences, one per row.

        Returns:
            The ``sqlite3.Cursor`` produced by the batch statement.

        Raises:
            sqlite3.Error: If execution fails.
        """
        try:
            cursor = self.connection.executemany(query, sequence)
            self._logger.debug(
                f"Executed many SQL ({len(sequence)} rows): {query.strip()}"
            )
            return cursor
        except sqlite3.Error:
            self._logger.exception(
                f"SQL executemany failed: {query.strip()}"
            )
            self.rollback()
            raise

    def fetchone(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> Optional[sqlite3.Row]:
        """
        Execute a query and return the first matching row.

        Args:
            query: SQL SELECT (or similar) with ``?`` placeholders.
            parameters: Values bound to the placeholders.

        Returns:
            A ``sqlite3.Row`` if a row exists; otherwise ``None``.

        Raises:
            sqlite3.Error: If execution fails.
        """
        cursor = self.execute(query, parameters)
        return cursor.fetchone()

    def fetchall(
        self,
        query: str,
        parameters: Sequence[Any] = (),
    ) -> list[sqlite3.Row]:
        """
        Execute a query and return all matching rows.

        Args:
            query: SQL SELECT (or similar) with ``?`` placeholders.
            parameters: Values bound to the placeholders.

        Returns:
            A list of ``sqlite3.Row`` objects (empty when no matches).

        Raises:
            sqlite3.Error: If execution fails.
        """
        cursor = self.execute(query, parameters)
        return cursor.fetchall()

    def commit(self) -> None:
        """
        Commit the current transaction.

        Raises:
            RuntimeError: If no connection is open.
            sqlite3.Error: If the commit fails.
        """
        if self._connection is None:
            raise RuntimeError("No database connection is open.")

        try:
            self._connection.commit()
            self._logger.debug("Database transaction committed.")
        except sqlite3.Error:
            self._logger.exception("Failed to commit database transaction.")
            raise

    def rollback(self) -> None:
        """
        Roll back the current transaction.

        Safe to call when no connection is open; logs and returns in that
        case. Logs failures without re-raising so callers performing
        cleanup after an error can proceed.
        """
        if self._connection is None:
            return

        try:
            self._connection.rollback()
            self._logger.warning("Database transaction rolled back.")
        except sqlite3.Error:
            self._logger.exception(
                "Failed to roll back database transaction."
            )

    def create_tables(self) -> None:
        """
        Create core ALCOS tables if they do not already exist.

        Creates ``users``, ``letters_of_credit``, ``amendments``,
        ``notifications``, and ``audit_logs``. Commits on success and
        rolls back on failure.

        Raises:
            sqlite3.Error: If schema creation fails.
        """
        try:
            for statement in _SCHEMA_STATEMENTS:
                self.connection.execute(statement)
            self.commit()
            self._logger.info("Database schema verified / created.")
        except sqlite3.Error:
            self._logger.exception("Failed to create database tables.")
            self.rollback()
            raise

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """
        Provide a transactional context manager around the connection.

        Commits on clean exit and rolls back if an exception propagates.

        Yields:
            The active ``sqlite3.Connection``.

        Raises:
            Exception: Re-raises any exception after rolling back.
        """
        conn = self.connection
        try:
            yield conn
            self.commit()
        except Exception:
            self.rollback()
            raise
