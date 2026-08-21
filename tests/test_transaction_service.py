from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.database import DatabaseManager
from app.services.transaction_service import TransactionService


class TransactionServiceTests(unittest.TestCase):
    """Save/update idempotency and workflow bootstrap tests."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_db = (
            Path(self.temp_dir.name)
            / "alcos_transaction_test.db"
        )

        self.db = DatabaseManager()
        self.db.disconnect()

        self.path_patch = patch(
            "app.core.database.DATABASE_PATH",
            self.test_db,
        )

        self.path_patch.start()

        self.db.connect()

        self.service = TransactionService()

    def tearDown(self):
        self.db.disconnect()
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def _save(self, lc_number, applicant="Applicant A", amount=100000):
        return self.service.create_transaction(
            "TXN-1",
            "REF-1",
            lc_number,
            applicant,
            "Beneficiary B",
            amount,
            "USD",
            "Draft",
            "2026-08-13",
            "2026-12-31",
        )

    def test_create_returns_lc_id_and_creates_workflow(self):
        lc_id = self._save("LC-IDEM-1")

        self.assertGreater(lc_id, 0)

        lc = self.db.fetchone(
            "SELECT * FROM letters_of_credit WHERE id = ?",
            (lc_id,),
        )

        self.assertIsNotNone(lc)
        self.assertEqual(lc["lc_number"], "LC-IDEM-1")

        workflow = self.db.fetchone(
            "SELECT * FROM lc_workflow_state WHERE lc_id = ?",
            (lc_id,),
        )

        self.assertIsNotNone(workflow)

    def test_resave_updates_same_lc_without_duplicate(self):
        first_id = self._save("LC-IDEM-2", amount=100000)

        second_id = self._save(
            "LC-IDEM-2", applicant="Updated Co", amount=250000
        )

        self.assertEqual(first_id, second_id)

        rows = self.db.fetchall(
            "SELECT * FROM letters_of_credit "
            "WHERE lc_number = 'LC-IDEM-2'"
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["applicant"], "Updated Co")
        self.assertEqual(rows[0]["amount"], 250000)

    def test_workflow_created_exactly_once_across_resaves(self):
        lc_id = self._save("LC-IDEM-3")
        self._save("LC-IDEM-3")
        self._save("LC-IDEM-3")

        workflows = self.db.fetchall(
            "SELECT * FROM lc_workflow_state WHERE lc_id = ?",
            (lc_id,),
        )

        self.assertEqual(len(workflows), 1)

    def test_missing_lc_number_rejected(self):
        with self.assertRaises(ValueError):
            self._save("   ")


if __name__ == "__main__":
    unittest.main()
