from __future__ import annotations

import unittest
from pathlib import Path

from app.core.context import ApplicationContext, get_context


class ApplicationContextTests(unittest.TestCase):
    """Contract tests for the shared frontend application context."""

    def setUp(self):
        self.context = ApplicationContext()

    #################################################################
    # Initial state
    #################################################################

    def test_initial_state_is_empty(self):
        self.assertIsNone(self.context.current_user)
        self.assertIsNone(self.context.current_role)
        self.assertIsNone(self.context.current_lc_id)
        self.assertIsNone(self.context.current_lc_number)
        self.assertFalse(self.context.has_user)
        self.assertFalse(self.context.has_lc)

    #################################################################
    # User identity
    #################################################################

    def test_set_user_emits_user_changed(self):
        seen = []

        self.context.userChanged.connect(
            lambda u, r: seen.append((u, r))
        )

        self.context.set_user("alice", "ADMIN")

        self.assertEqual(seen, [("alice", "ADMIN")])
        self.assertEqual(self.context.current_user, "alice")
        self.assertEqual(self.context.current_role, "ADMIN")
        self.assertTrue(self.context.has_user)

    def test_set_user_defaults_role(self):
        self.context.set_user("bob", "")

        self.assertEqual(self.context.current_role, "USER")

    def test_set_user_rejects_empty_username(self):
        with self.assertRaises(ValueError):
            self.context.set_user("   ", "ADMIN")

    def test_clear_user_emits_and_resets(self):
        self.context.set_user("alice", "ADMIN")

        seen = []
        self.context.userCleared.connect(
            lambda: seen.append(True)
        )

        self.context.clear_user()

        self.assertEqual(seen, [True])
        self.assertIsNone(self.context.current_user)
        self.assertIsNone(self.context.current_role)

    def test_clear_user_without_user_is_silent(self):
        seen = []
        self.context.userCleared.connect(
            lambda: seen.append(True)
        )

        self.context.clear_user()

        self.assertEqual(seen, [])

    #################################################################
    # Current LC
    #################################################################

    def test_set_current_lc_emits_with_values(self):
        seen = []

        self.context.currentLCChanged.connect(
            lambda i, n: seen.append((i, n))
        )

        self.context.set_current_lc(7, "LC202600001")

        self.assertEqual(seen, [(7, "LC202600001")])
        self.assertEqual(self.context.current_lc_id, 7)
        self.assertEqual(
            self.context.current_lc_number,
            "LC202600001",
        )
        self.assertTrue(self.context.has_lc)

    def test_set_current_lc_accepts_int_like_id(self):
        self.context.set_current_lc("42", "LC-X")

        self.assertEqual(self.context.current_lc_id, 42)

    def test_set_current_lc_rejects_bad_ids(self):
        for bad in (0, -1, None, "abc"):
            with self.assertRaises(ValueError):
                self.context.set_current_lc(bad, "LC-X")

    def test_set_current_lc_rejects_empty_number(self):
        with self.assertRaises(ValueError):
            self.context.set_current_lc(1, "   ")

    def test_switching_lc_leaves_no_stale_metadata(self):
        self.context.set_current_lc(
            1, "LC-OLD", {"applicant": "Old Co"}
        )
        self.context.set_current_lc(
            2, "LC-NEW", {"applicant": "New Co"}
        )

        metadata = self.context.lc_metadata

        self.assertEqual(metadata.get("applicant"), "New Co")
        self.assertNotIn("stale", metadata)

    def test_update_lc_metadata_merges_and_emits(self):
        seen = []
        self.context.lcMetadataChanged.connect(
            lambda: seen.append(True)
        )

        self.context.set_current_lc(5, "LC-5")
        self.context.update_lc_metadata({"stage_status": "IN_PROGRESS"})

        self.assertEqual(seen, [True])
        self.assertEqual(
            self.context.lc_metadata.get("stage_status"),
            "IN_PROGRESS",
        )

    def test_update_metadata_without_lc_is_ignored(self):
        seen = []
        self.context.lcMetadataChanged.connect(
            lambda: seen.append(True)
        )

        self.context.update_lc_metadata({"x": 1})

        self.assertEqual(seen, [])
        self.assertEqual(self.context.lc_metadata, {})

    def test_clear_current_lc_emits_and_resets(self):
        self.context.set_current_lc(3, "LC-3")

        seen = []
        self.context.currentLCCleared.connect(
            lambda: seen.append(True)
        )

        self.context.clear_current_lc()

        self.assertEqual(seen, [True])
        self.assertIsNone(self.context.current_lc_id)
        self.assertIsNone(self.context.current_lc_number)
        self.assertEqual(self.context.lc_metadata, {})

    def test_clear_without_lc_is_silent(self):
        seen = []
        self.context.currentLCCleared.connect(
            lambda: seen.append(True)
        )

        self.context.clear_current_lc()

        self.assertEqual(seen, [])

    def test_setting_same_lc_does_not_reemit_change(self):
        self.context.set_current_lc(3, "LC-3")

        seen = []
        self.context.currentLCChanged.connect(
            lambda i, n: seen.append((i, n))
        )

        self.context.set_current_lc(3, "LC-3")

        self.assertEqual(seen, [])

    #################################################################
    # Singleton + architecture boundary
    #################################################################

    def test_get_context_returns_same_instance(self):
        self.assertIs(get_context(), get_context())

    def test_services_do_not_import_context(self):
        """
        Architecture rule: services must stay independent of the
        frontend context so they remain reusable behind a server API.
        """
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import pathlib, sys;"
                    "bad=[str(p) for p in pathlib.Path('app/services')"
                    ".glob('*.py') "
                    "if p.name != '__init__.py' and "
                    "'app.core.context' in p.read_text(encoding='utf-8')];"
                    "print('\\n'.join(bad));"
                    "sys.exit(1 if bad else 0)"
                ),
            ],
            capture_output=True,
            text=True,
            cwd=".",
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "Service modules must not depend on "
                f"app.core.context: {result.stdout}"
            ),
        )

    def test_application_controller_uses_shared_context(self):
        """
        Regression guard: the controller must use the shared singleton
        context, never a private ApplicationContext instance, otherwise
        authentication would silently never reach the widgets.
        """
        source = Path("app/core/application.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn(
            "= ApplicationContext(",
            source,
            msg=(
                "ALCOSApplication must call get_context() instead of "
                "constructing a private ApplicationContext."
            ),
        )
        self.assertIn("get_context()", source)


if __name__ == "__main__":
    unittest.main()
