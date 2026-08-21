from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage, StageStatus
from app.services.lc_workflow_service import (
    InvalidWorkflowTransition,
    LCWorkflowService,
    WorkflowStageNotReady,
)


class LCWorkflowServiceTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.test_db = (
            Path(self.temp_dir.name)
            / "alcos_workflow_test.db"
        )

        self.db = DatabaseManager()
        self.db.disconnect()

        self.path_patch = patch(
            "app.core.database.DATABASE_PATH",
            self.test_db,
        )

        self.path_patch.start()

        self.db.connect()

        self.service = LCWorkflowService(self.db)

    def tearDown(self):
        self.db.disconnect()
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def create_lc(self, lc_number):
        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO letters_of_credit (
                    lc_number,
                    applicant,
                    beneficiary,
                    amount,
                    currency,
                    status,
                    issue_date,
                    expiry_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lc_number,
                    "Test Applicant",
                    "Test Beneficiary",
                    100000,
                    "USD",
                    "ACTIVE",
                    "2026-08-13",
                    "2026-12-31",
                ),
            )

            return int(cursor.lastrowid)

    def test_workflow_creation(self):
        lc_id = self.create_lc(
            "TEST-WORKFLOW-CREATE"
        )

        workflow = (
            self.service.create_workflow_for_lc(
                lc_id
            )
        )

        self.assertEqual(
            workflow["current_stage"],
            1,
        )

        self.assertEqual(
            workflow["stage_status"],
            "IN_PROGRESS",
        )

    def test_workflow_creation_is_idempotent(self):
        lc_id = self.create_lc(
            "TEST-IDEMPOTENT"
        )

        first = (
            self.service.create_workflow_for_lc(
                lc_id
            )
        )

        second = (
            self.service.create_workflow_for_lc(
                lc_id
            )
        )

        self.assertEqual(
            first["id"],
            second["id"],
        )

        history = (
            self.service.list_stage_history(
                lc_id
            )
        )

        created_events = [
            row
            for row in history
            if row["action"]
            == "WORKFLOW_CREATED"
        ]

        self.assertEqual(
            len(created_events),
            1,
        )

    def test_invalid_jump_is_blocked(self):
        lc_id = self.create_lc(
            "TEST-INVALID-JUMP"
        )

        self.service.create_workflow_for_lc(
            lc_id
        )

        with self.assertRaises(
            InvalidWorkflowTransition
        ):
            self.service.transition_stage(
                lc_id,
                LCStage.SCRUTINY,
            )

    def test_stage_must_be_complete(self):
        lc_id = self.create_lc(
            "TEST-NOT-READY"
        )

        self.service.create_workflow_for_lc(
            lc_id
        )

        with self.assertRaises(
            WorkflowStageNotReady
        ):
            self.service.transition_stage(
                lc_id,
                LCStage.PO_MATCHING,
            )

    def test_amendment_returns_to_scrutiny(self):
        lc_id = self.create_lc(
            "TEST-AMENDMENT"
        )

        self.service.create_workflow_for_lc(
            lc_id
        )

        self.service.record_stage_event(
            lc_id,
            LCStage.INTAKE,
            StageStatus.COMPLETED,
        )

        self.service.transition_stage(
            lc_id,
            LCStage.PO_MATCHING,
        )

        self.service.record_stage_event(
            lc_id,
            LCStage.PO_MATCHING,
            StageStatus.COMPLETED,
        )

        self.service.transition_stage(
            lc_id,
            LCStage.SCRUTINY,
        )

        self.service.record_stage_event(
            lc_id,
            LCStage.SCRUTINY,
            StageStatus.FAILED,
        )

        self.service.transition_stage(
            lc_id,
            LCStage.AMENDMENT,
        )

        self.service.record_stage_event(
            lc_id,
            LCStage.AMENDMENT,
            StageStatus.COMPLETED,
            action="AMENDED_LC_RECEIVED",
        )

        result = self.service.transition_stage(
            lc_id,
            LCStage.SCRUTINY,
        )

        self.assertEqual(
            result["current_stage"],
            3,
        )

    def test_payment_completion_closes_lc(self):
        lc_id = self.create_lc(
            "TEST-PAYMENT"
        )

        self.service.create_workflow_for_lc(
            lc_id
        )

        flow = [
            (
                LCStage.INTAKE,
                LCStage.PO_MATCHING,
                StageStatus.COMPLETED,
            ),
            (
                LCStage.PO_MATCHING,
                LCStage.SCRUTINY,
                StageStatus.COMPLETED,
            ),
            (
                LCStage.SCRUTINY,
                LCStage.DOCUMENTS,
                StageStatus.PASSED,
            ),
            (
                LCStage.DOCUMENTS,
                LCStage.BANK_SUBMISSION,
                StageStatus.COMPLETED,
            ),
            (
                LCStage.BANK_SUBMISSION,
                LCStage.DISCOUNTING,
                StageStatus.COMPLETED,
            ),
            (
                LCStage.DISCOUNTING,
                LCStage.PAYMENT_TRACKING,
                StageStatus.COMPLETED,
            ),
        ]

        for current, target, status in flow:
            self.service.record_stage_event(
                lc_id,
                current,
                status,
            )

            self.service.transition_stage(
                lc_id,
                target,
            )

        self.service.record_stage_event(
            lc_id,
            LCStage.PAYMENT_TRACKING,
            StageStatus.COMPLETED,
            action="PAYMENT_RECEIVED",
        )

        workflow = (
            self.service.get_workflow(
                lc_id
            )
        )

        self.assertEqual(
            workflow["current_stage"],
            8,
        )

        self.assertEqual(
            workflow["stage_status"],
            "COMPLETED",
        )

        self.assertEqual(
            workflow["overall_status"],
            "COMPLETED",
        )


if __name__ == "__main__":
    unittest.main()
