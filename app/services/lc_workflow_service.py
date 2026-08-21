"""
ALCOS LC Workflow Service
=========================

Backend lifecycle management for one Letter of Credit.

This service:
- creates one workflow per LC
- records workflow history
- validates stage transitions
- tracks human-review requirements
- closes the workflow after payment completion

It does not contain UI code.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Optional

from app.core.database import DatabaseManager
from app.core.lc_workflow import (
    LCStage,
    LCStatus,
    StageStatus,
    can_transition,
    stage_label,
)


class WorkflowError(RuntimeError):
    """Base workflow exception."""


class LCNotFoundError(WorkflowError):
    """Requested LC does not exist."""


class WorkflowNotFoundError(WorkflowError):
    """LC exists but has no workflow."""


class InvalidWorkflowTransition(WorkflowError):
    """Requested stage transition is not allowed."""


class WorkflowStageNotReady(WorkflowError):
    """Current stage status does not allow the requested transition."""


def _normalize_stage(stage: LCStage | int) -> LCStage:
    try:
        if isinstance(stage, LCStage):
            return stage
        return LCStage(int(stage))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid LC workflow stage: {stage!r}"
        ) from exc


def _normalize_status(
    status: StageStatus | str,
) -> StageStatus:
    try:
        if isinstance(status, StageStatus):
            return status
        return StageStatus(str(status))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid stage status: {status!r}"
        ) from exc


class LCWorkflowService:
    """Manage persisted LC lifecycle state."""

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
    ):
        self.db = db or DatabaseManager()

    @staticmethod
    def _ensure_lc_exists(
        conn: sqlite3.Connection,
        lc_id: int,
    ) -> None:
        row = conn.execute(
            """
            SELECT id
            FROM letters_of_credit
            WHERE id = ?
            """,
            (lc_id,),
        ).fetchone()

        if row is None:
            raise LCNotFoundError(
                f"LC id {lc_id} does not exist."
            )

    def _create_in_connection(
        self,
        conn: sqlite3.Connection,
        lc_id: int,
    ) -> dict[str, Any]:

        self._ensure_lc_exists(conn, lc_id)

        cursor = conn.execute(
            """
            INSERT INTO lc_workflow_state (
                lc_id,
                current_stage,
                stage_status,
                overall_status,
                requires_human_review,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, 0,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP)
            ON CONFLICT(lc_id) DO NOTHING
            """,
            (
                lc_id,
                int(LCStage.INTAKE),
                StageStatus.IN_PROGRESS.value,
                LCStatus.ACTIVE.value,
            ),
        )

        created = cursor.rowcount == 1

        if created:
            conn.execute(
                """
                INSERT INTO lc_stage_history (
                    lc_id,
                    stage,
                    status,
                    action,
                    notes,
                    performed_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP)
                """,
                (
                    lc_id,
                    int(LCStage.INTAKE),
                    StageStatus.IN_PROGRESS.value,
                    "WORKFLOW_CREATED",
                    "LC workflow created and intake started.",
                    "SYSTEM",
                ),
            )

        row = conn.execute(
            """
            SELECT *
            FROM lc_workflow_state
            WHERE lc_id = ?
            """,
            (lc_id,),
        ).fetchone()

        if row is None:
            raise WorkflowNotFoundError(
                f"Workflow could not be loaded "
                f"for LC id {lc_id}."
            )

        return dict(row)

    def create_workflow_for_lc(
        self,
        lc_id: int,
        *,
        connection: Optional[
            sqlite3.Connection
        ] = None,
    ) -> dict[str, Any]:
        """
        Create one workflow for the LC.

        Safe to call repeatedly because lc_id is UNIQUE.
        """

        if connection is not None:
            return self._create_in_connection(
                connection,
                lc_id,
            )

        with self.db.transaction() as conn:
            return self._create_in_connection(
                conn,
                lc_id,
            )

    def get_workflow(
        self,
        lc_id: int,
    ) -> Optional[dict[str, Any]]:

        row = self.db.fetchone(
            """
            SELECT *
            FROM lc_workflow_state
            WHERE lc_id = ?
            """,
            (lc_id,),
        )

        if row is None:
            return None

        return dict(row)

    def list_stage_history(
        self,
        lc_id: int,
    ) -> list[dict[str, Any]]:

        rows = self.db.fetchall(
            """
            SELECT *
            FROM lc_stage_history
            WHERE lc_id = ?
            ORDER BY id ASC
            """,
            (lc_id,),
        )

        return [dict(row) for row in rows]

    def record_stage_event(
        self,
        lc_id: int,
        stage: LCStage | int,
        status: StageStatus | str,
        *,
        action: Optional[str] = None,
        notes: Optional[str] = None,
        performed_by: Optional[str] = None,
    ) -> dict[str, Any]:

        stage = _normalize_stage(stage)
        status = _normalize_status(status)

        with self.db.transaction() as conn:

            workflow = conn.execute(
                """
                SELECT *
                FROM lc_workflow_state
                WHERE lc_id = ?
                """,
                (lc_id,),
            ).fetchone()

            if workflow is None:
                raise WorkflowNotFoundError(
                    f"No workflow exists "
                    f"for LC id {lc_id}."
                )

            cursor = conn.execute(
                """
                INSERT INTO lc_stage_history (
                    lc_id,
                    stage,
                    status,
                    action,
                    notes,
                    performed_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP)
                """,
                (
                    lc_id,
                    int(stage),
                    status.value,
                    action or status.value,
                    notes,
                    performed_by or "SYSTEM",
                ),
            )

            event_id = int(cursor.lastrowid)

            if int(
                workflow["current_stage"]
            ) == int(stage):

                human_review = (
                    1
                    if status in {
                        StageStatus.FAILED,
                        StageStatus.WAITING_HUMAN,
                    }
                    else 0
                )

                overall_status = str(
                    workflow["overall_status"]
                )

                if (
                    stage
                    == LCStage.PAYMENT_TRACKING
                    and status
                    == StageStatus.COMPLETED
                ):
                    overall_status = (
                        LCStatus.COMPLETED.value
                    )

                conn.execute(
                    """
                    UPDATE lc_workflow_state
                    SET
                        stage_status = ?,
                        overall_status = ?,
                        requires_human_review = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE lc_id = ?
                    """,
                    (
                        status.value,
                        overall_status,
                        human_review,
                        lc_id,
                    ),
                )

            event = conn.execute(
                """
                SELECT *
                FROM lc_stage_history
                WHERE id = ?
                """,
                (event_id,),
            ).fetchone()

        return dict(event)

    @staticmethod
    def _status_allows_transition(
        current: LCStage,
        target: LCStage,
        status: StageStatus,
    ) -> bool:
        """
        Business gate in addition to structural transition rules.
        """

        if (
            current == LCStage.SCRUTINY
            and target == LCStage.AMENDMENT
        ):
            return status == StageStatus.FAILED

        if (
            current == LCStage.SCRUTINY
            and target == LCStage.DOCUMENTS
        ):
            return status in {
                StageStatus.PASSED,
                StageStatus.COMPLETED,
            }

        if current == LCStage.AMENDMENT:
            return status == StageStatus.COMPLETED

        return status in {
            StageStatus.PASSED,
            StageStatus.COMPLETED,
            StageStatus.NOT_REQUIRED,
        }

    def transition_stage(
        self,
        lc_id: int,
        next_stage: LCStage | int,
        *,
        action: Optional[str] = None,
        notes: Optional[str] = None,
        performed_by: Optional[str] = None,
    ) -> dict[str, Any]:

        target = _normalize_stage(next_stage)

        with self.db.transaction() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM lc_workflow_state
                WHERE lc_id = ?
                """,
                (lc_id,),
            ).fetchone()

            if row is None:
                raise WorkflowNotFoundError(
                    f"No workflow exists "
                    f"for LC id {lc_id}."
                )

            current = LCStage(
                int(row["current_stage"])
            )

            current_status = StageStatus(
                str(row["stage_status"])
            )

            if current == target:
                return dict(row)

            if not can_transition(
                current,
                target,
            ):
                raise InvalidWorkflowTransition(
                    f"Illegal transition: "
                    f"{stage_label(current)} -> "
                    f"{stage_label(target)}"
                )

            if not self._status_allows_transition(
                current,
                target,
                current_status,
            ):
                raise WorkflowStageNotReady(
                    f"{stage_label(current)} "
                    f"has status "
                    f"{current_status.value}; "
                    f"cannot move to "
                    f"{stage_label(target)}."
                )

            conn.execute(
                """
                UPDATE lc_workflow_state
                SET
                    current_stage = ?,
                    stage_status = ?,
                    requires_human_review = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE lc_id = ?
                """,
                (
                    int(target),
                    StageStatus.IN_PROGRESS.value,
                    lc_id,
                ),
            )

            conn.execute(
                """
                INSERT INTO lc_stage_history (
                    lc_id,
                    stage,
                    status,
                    action,
                    notes,
                    performed_by,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP)
                """,
                (
                    lc_id,
                    int(target),
                    StageStatus.IN_PROGRESS.value,
                    action
                    or (
                        f"TRANSITION_"
                        f"{current.name}_TO_"
                        f"{target.name}"
                    ),
                    notes,
                    performed_by or "SYSTEM",
                ),
            )

            updated = conn.execute(
                """
                SELECT *
                FROM lc_workflow_state
                WHERE lc_id = ?
                """,
                (lc_id,),
            ).fetchone()

        return dict(updated)


_default_service = LCWorkflowService()


def create_workflow_for_lc(
    lc_id: int,
    *,
    connection: Optional[
        sqlite3.Connection
    ] = None,
) -> dict[str, Any]:

    return _default_service.create_workflow_for_lc(
        lc_id,
        connection=connection,
    )


def get_workflow(
    lc_id: int,
) -> Optional[dict[str, Any]]:

    return _default_service.get_workflow(lc_id)


def record_stage_event(
    lc_id: int,
    stage: LCStage | int,
    status: StageStatus | str,
    *,
    action: Optional[str] = None,
    notes: Optional[str] = None,
    performed_by: Optional[str] = None,
) -> dict[str, Any]:

    return _default_service.record_stage_event(
        lc_id,
        stage,
        status,
        action=action,
        notes=notes,
        performed_by=performed_by,
    )


def transition_stage(
    lc_id: int,
    next_stage: LCStage | int,
    *,
    action: Optional[str] = None,
    notes: Optional[str] = None,
    performed_by: Optional[str] = None,
) -> dict[str, Any]:

    return _default_service.transition_stage(
        lc_id,
        next_stage,
        action=action,
        notes=notes,
        performed_by=performed_by,
    )


def list_stage_history(
    lc_id: int,
) -> list[dict[str, Any]]:

    return _default_service.list_stage_history(
        lc_id
    )
