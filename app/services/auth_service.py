"""
ALCOS Authentication Service
============================

Local desktop authentication for ALCOS.

- Passwords are hashed with scrypt (stdlib ``hashlib``) using a unique
  random salt per hash. The stored format is self-describing:
  ``scrypt$<n>$<r>$<p>$<salt_hex>$<dk_hex>``
- Verification uses constant-time comparison (``hmac.compare_digest``).
- The legacy ``users.password`` column is never read or written; the
  schema migration below only ADDS a nullable ``password_hash`` column
  and is idempotent and non-destructive.
- First-run bootstrap: while no users exist, the login screen offers an
  explicit "Create Initial Administrator" flow. Once any user exists the
  bootstrap path is permanently unavailable.
- Audit events (LOGIN_SUCCESS / LOGIN_FAILURE / ADMIN_BOOTSTRAP_CREATED)
  are written to ``audit_logs``. Passwords are never stored in plaintext,
  never logged, and never included in error messages.

This module contains no GUI code and does not depend on the application
context. Callers pass explicit parameters so the service remains reusable
behind a future server boundary.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import sqlite3
from dataclasses import dataclass
from typing import Optional

from app.core.database import DatabaseManager
from app.core.logger import LoggerManager

# scrypt work factors (OWASP-recommended baseline).
_SCRYPT_N = 2 ** 14
_SCRYPT_R = 8
_SCRYPT_P = 1
_DKLEN = 64
_SALT_BYTES = 16

# Local password policy for the desktop prototype.
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

_HASH_PREFIX = "scrypt"


class AuthError(RuntimeError):
    """Base authentication/bootstrap error."""


class UserExistsError(AuthError):
    """The requested username is already taken."""


class BootstrapUnavailableError(AuthError):
    """Bootstrap was attempted although users already exist."""


@dataclass(frozen=True)
class AuthResult:
    """Outcome of an authentication attempt."""

    success: bool
    username: Optional[str] = None
    role: Optional[str] = None
    error: Optional[str] = None


def _hash_password(password: str) -> str:
    """Hash a password with scrypt and a unique random salt."""
    salt = os.urandom(_SALT_BYTES)

    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_DKLEN,
    )

    return (
        f"{_HASH_PREFIX}${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}"
        f"${salt.hex()}${digest.hex()}"
    )


def _verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored scrypt hash.

    Constant-time comparison; returns False for malformed hashes rather
    than raising, so corrupted rows simply fail authentication.
    """
    try:
        prefix, n, r, p, salt_hex, dk_hex = stored_hash.split("$")
    except (ValueError, AttributeError):
        return False

    if prefix != _HASH_PREFIX:
        return False

    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(digest, expected)


class AuthService:
    """Local authentication and first-admin bootstrap."""

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or DatabaseManager()
        self.logger = LoggerManager()

        # Additive, idempotent migration for hashed credentials.
        # A single guarded PRAGMA check per construction; repeated
        # invocations are no-ops.
        self.ensure_schema()

    #################################################################
    # Schema (additive, idempotent, non-destructive)
    #################################################################

    def ensure_schema(self) -> None:
        """
        Add the ``password_hash`` column when missing.

        Idempotent: repeated calls are no-ops. The legacy ``password``
        column and all existing rows are left untouched.
        """
        columns = self.db.fetchall("PRAGMA table_info(users)")

        if not columns:
            raise AuthError("users table does not exist.")

        if any(row["name"] == "password_hash" for row in columns):
            return

        try:
            with self.db.transaction() as conn:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN password_hash TEXT"
                )
            self.logger.info(
                "Auth schema migrated: added users.password_hash."
            )
        except sqlite3.Error as exc:
            self.logger.exception("Failed to add users.password_hash.")
            raise AuthError("Password-hash migration failed.") from exc

    #################################################################
    # Queries
    #################################################################

    def has_any_user(self) -> bool:
        """Whether at least one user account exists."""
        row = self.db.fetchone("SELECT COUNT(*) AS n FROM users")
        return bool(row and int(row["n"]) > 0)

    #################################################################
    # First-admin bootstrap
    #################################################################

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate and normalize a username; raises AuthError."""
        clean = str(username or "").strip()

        if not _USERNAME_PATTERN.match(clean):
            raise AuthError(
                "Username must be 3-32 characters and may contain "
                "letters, digits, dot, underscore or hyphen."
            )

        return clean

    @staticmethod
    def validate_password(password: str, confirmation: str) -> None:
        """Validate a new password and its confirmation; raises AuthError."""
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise AuthError(
                f"Password must be at least "
                f"{MIN_PASSWORD_LENGTH} characters long."
            )

        if len(password) > MAX_PASSWORD_LENGTH:
            raise AuthError(
                f"Password must be at most "
                f"{MAX_PASSWORD_LENGTH} characters long."
            )

        if password != confirmation:
            raise AuthError("Password and confirmation do not match.")

    def create_initial_admin(
        self,
        username: str,
        password: str,
        confirmation: str,
    ) -> int:
        """
        Create the first ADMIN account.

        Only permitted while no users exist. Rejected afterwards so a
        repeated startup can never recreate or overwrite the bootstrap
        administrator.

        Returns:
            The new user id.

        Raises:
            AuthError: Invalid username/password/confirmation.
            UserExistsError: Username already taken.
            BootstrapUnavailableError: Users already exist.
        """
        if self.has_any_user():
            raise BootstrapUnavailableError(
                "Initial administrator already exists. "
                "Please sign in instead."
            )

        clean_name = self.validate_username(username)
        self.validate_password(password, confirmation)

        password_hash = _hash_password(password)

        try:
            with self.db.transaction() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (
                        username,
                        password_hash,
                        role,
                        created_at
                    )
                    VALUES (?, ?, 'ADMIN', CURRENT_TIMESTAMP)
                    """,
                    (clean_name, password_hash),
                )
                user_id = int(cursor.lastrowid)

        except sqlite3.IntegrityError as exc:
            raise UserExistsError(
                f"Username '{clean_name}' is already taken."
            ) from exc

        self._audit(clean_name, "ADMIN_BOOTSTRAP_CREATED")
        self.logger.info(
            f"Initial administrator '{clean_name}' created."
        )

        return user_id

    #################################################################
    # Authentication
    #################################################################

    def authenticate(self, username: str, password: str) -> AuthResult:
        """
        Verify credentials against the hashed password column.

        Never stores, logs, or embeds the password anywhere. Failure
        messages do not reveal whether the username exists.
        """
        clean_name = str(username or "").strip()
        clean_password = str(password or "")

        if not clean_name or not clean_password:
            self._audit(clean_name or "(empty)", "LOGIN_FAILURE")
            return AuthResult(
                success=False,
                error="Enter both username and password.",
            )

        try:
            row = self.db.fetchone(
                """
                SELECT username, role, password_hash
                FROM users
                WHERE username = ?
                """,
                (clean_name,),
            )
        except sqlite3.Error:
            self.logger.exception("Authentication lookup failed.")
            return AuthResult(
                success=False,
                error="Authentication is temporarily unavailable.",
            )

        if row is None or not row["password_hash"]:
            self._audit(clean_name, "LOGIN_FAILURE")
            return AuthResult(
                success=False,
                error="Invalid username or password.",
            )

        if not _verify_password(clean_password, row["password_hash"]):
            self._audit(clean_name, "LOGIN_FAILURE")
            return AuthResult(
                success=False,
                error="Invalid username or password.",
            )

        role = (row["role"] or "USER").strip() or "USER"

        self._audit(clean_name, "LOGIN_SUCCESS")
        self.logger.info(f"User '{clean_name}' authenticated.")

        return AuthResult(
            success=True,
            username=clean_name,
            role=role,
        )

    #################################################################
    # Audit helper
    #################################################################

    def _audit(self, username: str, action: str) -> None:
        """Write a security audit event. Never include secrets."""
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO audit_logs (username, action, timestamp)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (username, action),
                )
        except sqlite3.Error:
            # Audit failure must not block authentication itself.
            self.logger.exception(
                f"Failed to write audit event '{action}'."
            )
