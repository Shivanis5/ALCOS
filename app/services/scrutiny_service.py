"""
ALCOS Scrutiny Service
======================

Stage 3 backend orchestration.

Combines the business outcomes of:
- Validation
- Risk
- Compliance
- Discrepancy checking

Detailed validation/risk/compliance engines remain in
their existing dedicated services.
"""

from __future__ import annotations

from typing import Optional

from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage, StageStatus
from app.services.lc_workflow_service import (
    LCWorkflowService,
)


class ScrutinyError(RuntimeError):
    """Base scrutiny error."""


class ScrutinyStageError(ScrutinyError):
    """LC is not currently in Scrutiny."""


class ScrutinyService:

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
    ):
        self.db = db or DatabaseManager()
        self.workflow = LCWorkflowService(
            self.db
        )

    def evaluate(
        self,
        lc_id: int,
        *,
        validation_status: str,
        risk_level: str,
        compliance_status: str,
        risk_score: float | None = None,
        discrepancy_count: int = 0,
        notes: str | None = None,
        performed_by: str = "SYSTEM",
    ) -> dict:

        workflow = self.workflow.get_workflow(
            lc_id
        )

        if workflow is None:
            raise ScrutinyError(
                f"No workflow exists for LC {lc_id}."
            )

        if (
            int(workflow["current_stage"])
            != int(LCStage.SCRUTINY)
        ):
            raise ScrutinyStageError(
                "LC is not currently in Scrutiny."
            )

        validation = (
            validation_status
            .strip()
            .upper()
        )

        risk = (
            risk_level
            .strip()
            .upper()
        )

        compliance = (
            compliance_status
            .strip()
            .upper()
        )

        discrepancies = max(
            0,
            int(discrepancy_count),
        )

        if (
            compliance in {
                "FAILED",
                "FAIL",
                "BLOCKED",
            }
            or validation in {
                "FAILED",
                "FAIL",
            }
            or discrepancies > 0
        ):
            decision = "AMENDMENT_REQUIRED"
            stage_status = StageStatus.FAILED

        elif risk in {
            "HIGH",
            "CRITICAL",
        }:
            decision = "HUMAN_REVIEW_REQUIRED"
            stage_status = (
                StageStatus.WAITING_HUMAN
            )

        else:
            decision = "PASSED"
            stage_status = StageStatus.PASSED

        with self.db.transaction() as conn:

            cursor = conn.execute(
                """
                INSERT INTO lc_scrutiny_results (
                    lc_id,
                    validation_status,
                    risk_level,
                    risk_score,
                    compliance_status,
                    discrepancy_count,
                    decision,
                    notes,
                    performed_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP)
                """,
                (
                    lc_id,
                    validation,
                    risk,
                    risk_score,
                    compliance,
                    discrepancies,
                    decision,
                    notes,
                    performed_by,
                ),
            )

            result_id = int(
                cursor.lastrowid
            )

        self.workflow.record_stage_event(
            lc_id,
            LCStage.SCRUTINY,
            stage_status,
            action=(
                "SCRUTINY_" + decision
            ),
            notes=notes,
            performed_by=performed_by,
        )

        result = self.db.fetchone(
            """
            SELECT *
            FROM lc_scrutiny_results
            WHERE id = ?
            """,
            (result_id,),
        )

        return dict(result)

    def get_latest_result(
        self,
        lc_id: int,
    ) -> Optional[dict]:

        row = self.db.fetchone(
            """
            SELECT *
            FROM lc_scrutiny_results
            WHERE lc_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (lc_id,),
        )

        return (
            dict(row)
            if row is not None
            else None
        )
