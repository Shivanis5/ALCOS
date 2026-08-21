from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.database import DatabaseManager
from app.services.auth_service import (
    AuthError,
    AuthService,
    BootstrapUnavailableError,
    _hash_password,
    _verify_password,
)


class AuthServiceTests(unittest.TestCase):
    """Authentication, first-admin bootstrap and migration tests."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_db = (
            Path(self.temp_dir.name)
            / "alcos_auth_test.db"
        )

        self.db = DatabaseManager()
        self.db.disconnect()

        self.path_patch = patch(
            "app.core.database.DATABASE_PATH",
            self.test_db,
        )

        self.path_patch.start()

        self.db.connect()

        self._service = None

    def tearDown(self):
        self.db.disconnect()
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def service(self) -> AuthService:
        """Lazily construct the service (constructor runs migration)."""
        if self._service is None:
            self._service = AuthService(self.db)
        return self._service

    def _bootstrap_admin(self):
        self.service().create_initial_admin(
            "admin", "S3curePass!", "S3curePass!"
        )

    #################################################################
    # Schema migration
    #################################################################

    def test_ensure_schema_adds_password_hash_column(self):
        # No service constructed yet -> no migration has run.
        columns_before = {
            row["name"]
            for row in self.db.fetchall(
                "PRAGMA table_info(users)"
            )
        }

        self.assertNotIn("password_hash", columns_before)

        self.service()

        columns_after = {
            row["name"]
            for row in self.db.fetchall(
                "PRAGMA table_info(users)"
            )
        }

        self.assertIn("password_hash", columns_after)

        # Legacy column must remain untouched.
        self.assertIn("password", columns_after)

    def test_migration_is_idempotent_and_preserves_rows(self):
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    username, password, role, created_at
                )
                VALUES ('legacy', 'legacy-plain', 'USER',
                        CURRENT_TIMESTAMP)
                """
            )

        self.service()
        # Repeated invocation must be a no-op, not an error.
        self.service().ensure_schema()

        row = self.db.fetchone(
            "SELECT username, password FROM users "
            "WHERE username = 'legacy'"
        )

        self.assertIsNotNone(row)
        self.assertEqual(row["password"], "legacy-plain")

        columns = {
            r["name"]
            for r in self.db.fetchall("PRAGMA table_info(users)")
        }

        self.assertIn("password_hash", columns)

    #################################################################
    # Bootstrap
    #################################################################

    def test_no_users_initially(self):
        self.assertFalse(self.service().has_any_user())

    def test_create_initial_admin_success(self):
        user_id = self.service().create_initial_admin(
            "admin",
            "S3curePass!",
            "S3curePass!",
        )

        self.assertGreater(user_id, 0)
        self.assertTrue(self.service().has_any_user())

        row = self.db.fetchone(
            "SELECT role, password_hash FROM users WHERE id = ?",
            (user_id,),
        )

        self.assertEqual(row["role"], "ADMIN")
        self.assertTrue(row["password_hash"].startswith("scrypt$"))

    def test_bootstrap_impossible_once_any_user_exists(self):
        """
        Repeated startup / second-run bootstrap attempts must never
        recreate or overwrite the initial administrator.
        """
        self._bootstrap_admin()

        with self.assertRaises(BootstrapUnavailableError):
            self.service().create_initial_admin(
                "second", "Another-P1", "Another-P1"
            )

        with self.assertRaises(BootstrapUnavailableError):
            self.service().create_initial_admin(
                "admin", "S3curePass!", "S3curePass!"
            )

        users = self.db.fetchall("SELECT * FROM users")

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "admin")

    def test_database_rejects_duplicate_username(self):
        """
        The UNIQUE constraint backstops duplicate usernames for any
        future account-creation feature beyond Phase 1 bootstrap.
        """
        import sqlite3

        self._bootstrap_admin()

        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO users (
                        username, password_hash, role, created_at
                    )
                    VALUES ('admin', NULL, 'USER',
                            CURRENT_TIMESTAMP)
                    """
                )

    def test_bootstrap_rejects_short_password(self):
        with self.assertRaises(AuthError):
            self.service().create_initial_admin(
                "admin", "short", "short"
            )

    def test_bootstrap_rejects_mismatched_confirmation(self):
        with self.assertRaises(AuthError):
            self.service().create_initial_admin(
                "admin",
                "S3curePass!",
                "Different1",
            )

    def test_bootstrap_rejects_invalid_username(self):
        for bad in ("", "ab", "has space", "way-too-long-" * 4):
            with self.assertRaises(AuthError):
                self.service().create_initial_admin(
                    bad, "S3curePass!", "S3curePass!"
                )

    def test_plaintext_password_never_stored(self):
        self._bootstrap_admin()

        rows = self.db.fetchall("SELECT * FROM users")

        for row in rows:
            for value in tuple(row):
                if isinstance(value, str):
                    self.assertNotIn(
                        "S3curePass!",
                        value,
                        msg="Plaintext password found in users row.",
                    )

    def test_unique_salts_per_hash(self):
        hash_a = _hash_password("Password-1")
        hash_b = _hash_password("Password-1")

        self.assertNotEqual(hash_a, hash_b)
        self.assertTrue(_verify_password("Password-1", hash_a))
        self.assertTrue(_verify_password("Password-1", hash_b))

    def test_verify_rejects_malformed_hashes(self):
        self.assertFalse(_verify_password("x", ""))
        self.assertFalse(_verify_password("x", None))
        self.assertFalse(_verify_password("x", "plain-text"))
        self.assertFalse(
            _verify_password("x", "md5$1$2$zz$yy")
        )

    #################################################################
    # Authentication
    #################################################################

    def test_authenticate_success(self):
        self._bootstrap_admin()

        result = self.service().authenticate(
            "admin", "S3curePass!"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.username, "admin")
        self.assertEqual(result.role, "ADMIN")
        self.assertIsNone(result.error)

    def test_authenticate_wrong_password_fails(self):
        self._bootstrap_admin()

        result = self.service().authenticate("admin", "WrongPass9")

        self.assertFalse(result.success)
        self.assertIsNone(result.username)

    def test_authenticate_unknown_username_fails(self):
        self._bootstrap_admin()

        result = self.service().authenticate("ghost", "S3curePass!")

        self.assertFalse(result.success)

    def test_authenticate_empty_credentials_fail(self):
        result = self.service().authenticate("", "")

        self.assertFalse(result.success)

    def test_failure_messages_do_not_leak_user_existence(self):
        self._bootstrap_admin()

        unknown = self.service().authenticate(
            "ghost", "Whatever1"
        ).error

        wrong_password = self.service().authenticate(
            "admin", "WrongPass9"
        ).error

        self.assertEqual(unknown, wrong_password)

    def test_legacy_plaintext_row_cannot_authenticate(self):
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    username, password, role, created_at
                )
                VALUES ('legacy', 'legacy-plain', 'USER',
                        CURRENT_TIMESTAMP)
                """
            )

        result = self.service().authenticate(
            "legacy", "legacy-plain"
        )

        self.assertFalse(result.success)

    #################################################################
    # Audit trail
    #################################################################

    def test_audit_events_written(self):
        self._bootstrap_admin()

        self.service().authenticate("admin", "S3curePass!")
        self.service().authenticate("admin", "WrongPass9")
        self.service().authenticate("ghost", "Whatever1")

        actions = [
            row["action"]
            for row in self.db.fetchall(
                "SELECT action FROM audit_logs ORDER BY id"
            )
        ]

        self.assertIn("ADMIN_BOOTSTRAP_CREATED", actions)
        self.assertIn("LOGIN_SUCCESS", actions)
        self.assertIn("LOGIN_FAILURE", actions)

    def test_audit_never_contains_password(self):
        self._bootstrap_admin()

        self.service().authenticate("admin", "S3curePass!")
        self.service().authenticate("admin", "WrongPass9")

        for row in self.db.fetchall(
            "SELECT * FROM audit_logs"
        ):
            for value in tuple(row):
                if isinstance(value, str):
                    self.assertNotIn("S3curePass!", value)
                    self.assertNotIn("WrongPass9", value)


if __name__ == "__main__":
    unittest.main()
