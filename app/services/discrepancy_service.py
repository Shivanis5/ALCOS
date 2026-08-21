from __future__ import annotations

from typing import Optional

from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage
from app.services.lc_workflow_service import LCWorkflowService


class DiscrepancyError(RuntimeError):
    """Base discrepancy exception."""


class DiscrepancyService:
    """
    Stage 4 discrepancy persistence and resolution.
    """

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
    ):
        self.db = db or DatabaseManager()
        self.workflow = LCWorkflowService(self.db)

    def create_discrepancy(
        self,
        lc_id: int,
        *,
        discrepancy_type: str,
        severity: str,
        field_reference: str | None = None,
        current_text: str | None = None,
        required_text: str | None = None,
        reason: str | None = None,
        created_by: str = "USER",
    ) -> int:

        workflow = self.workflow.get_workflow(lc_id)

        if workflow is None:
            raise DiscrepancyError(
                "No workflow exists for this LC."
            )

        if int(workflow["current_stage"]) != int(
            LCStage.AMENDMENT
        ):
            raise DiscrepancyError(
                "This LC is not currently in "
                "Stage 4 — Amendments."
            )

        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO lc_discrepancies (
                    lc_id,
                    discrepancy_type,
                    severity,
                    field_reference,
                    current_text,
                    required_text,
                    reason,
                    status,
                    created_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?,
                        CURRENT_TIMESTAMP)
                """,
                (
                    lc_id,
                    discrepancy_type.strip().upper(),
                    severity.strip().upper(),
                    field_reference,
                    current_text,
                    required_text,
                    reason,
                    created_by,
                ),
            )

            return int(cursor.lastrowid)

    def list_discrepancies(
        self,
        lc_id: int,
    ) -> list[dict]:

        rows = self.db.fetchall(
            """
            SELECT *
            FROM lc_discrepancies
            WHERE lc_id = ?
            ORDER BY id DESC
            """,
            (lc_id,),
        )

        return [dict(row) for row in rows]

    def resolve_discrepancy(
        self,
        discrepancy_id: int,
    ) -> None:

        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE lc_discrepancies
                SET
                    status = 'RESOLVED',
                    resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (discrepancy_id,),
            )

            if cursor.rowcount != 1:
                raise DiscrepancyError(
                    "Discrepancy not found."
                )
