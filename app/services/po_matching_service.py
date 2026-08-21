"""
ALCOS PO Matching Service
=========================

Local prototype for Stage 2 - PO Matching.

The service:
- stores local purchase orders
- compares one LC against available POs
- returns ranked candidate matches
- stores the top candidates
- allows one PO to be selected

Future SAP/ERP adapters can feed purchase orders into the same model.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Optional

from app.core.database import DatabaseManager
from app.core.lc_workflow import LCStage, StageStatus
from app.services.lc_workflow_service import (
    LCWorkflowService,
    WorkflowNotFoundError,
)


class POMatchingError(RuntimeError):
    """Base PO matching error."""


class PurchaseOrderNotFoundError(POMatchingError):
    """Requested PO does not exist."""


class LCNotFoundForMatchingError(POMatchingError):
    """Requested LC does not exist."""


def _clean(value) -> str:
    if value is None:
        return ""

    return " ".join(
        str(value).strip().lower().split()
    )


def _text_score(left, right) -> float:
    left = _clean(left)
    right = _clean(right)

    if not left or not right:
        return 0.0

    return round(
        SequenceMatcher(
            None,
            left,
            right,
        ).ratio() * 100,
        2,
    )


def _currency_score(left, right) -> float:
    if not left or not right:
        return 0.0

    return (
        100.0
        if str(left).strip().upper()
        == str(right).strip().upper()
        else 0.0
    )


def _amount_score(lc_amount, po_amount) -> float:
    try:
        left = float(lc_amount)
        right = float(po_amount)
    except (TypeError, ValueError):
        return 0.0

    if left <= 0 or right <= 0:
        return 0.0

    difference = abs(left - right)
    base = max(left, right)

    percentage_difference = (
        difference / base
    )

    return round(
        max(
            0.0,
            100.0
            - percentage_difference * 100.0,
        ),
        2,
    )


def _date_score(left, right) -> float:
    if not left or not right:
        return 0.0

    return (
        100.0
        if str(left).strip()
        == str(right).strip()
        else 50.0
    )


class POMatchingService:

    def __init__(
        self,
        db: Optional[DatabaseManager] = None,
    ):
        self.db = db or DatabaseManager()
        self.workflow = LCWorkflowService(
            self.db
        )

    def create_purchase_order(
        self,
        po_number,
        applicant,
        beneficiary,
        amount,
        currency,
        issue_date=None,
        delivery_date=None,
        status="OPEN",
        source_system="LOCAL",
    ) -> int:

        with self.db.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO purchase_orders (
                    po_number,
                    applicant,
                    beneficiary,
                    amount,
                    currency,
                    issue_date,
                    delivery_date,
                    status,
                    source_system,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP)
                """,
                (
                    po_number,
                    applicant,
                    beneficiary,
                    amount,
                    currency,
                    issue_date,
                    delivery_date,
                    status,
                    source_system,
                ),
            )

            return int(cursor.lastrowid)

    def find_candidates(
        self,
        lc_id: int,
        limit: int = 3,
    ) -> list[dict]:

        lc = self.db.fetchone(
            """
            SELECT *
            FROM letters_of_credit
            WHERE id = ?
            """,
            (lc_id,),
        )

        if lc is None:
            raise LCNotFoundForMatchingError(
                f"LC id {lc_id} does not exist."
            )

        purchase_orders = self.db.fetchall(
            """
            SELECT *
            FROM purchase_orders
            WHERE status = 'OPEN'
            ORDER BY id ASC
            """
        )

        scored = []

        for po in purchase_orders:

            applicant_score = _text_score(
                lc["applicant"],
                po["applicant"],
            )

            beneficiary_score = _text_score(
                lc["beneficiary"],
                po["beneficiary"],
            )

            amount_score = _amount_score(
                lc["amount"],
                po["amount"],
            )

            currency_score = _currency_score(
                lc["currency"],
                po["currency"],
            )

            date_score = _date_score(
                lc["issue_date"],
                po["issue_date"],
            )

            total = round(
                applicant_score * 0.20
                + beneficiary_score * 0.25
                + amount_score * 0.25
                + currency_score * 0.20
                + date_score * 0.10,
                2,
            )

            scored.append(
                {
                    "po_id": int(po["id"]),
                    "po_number": po["po_number"],
                    "match_score": total,
                    "applicant_score": applicant_score,
                    "beneficiary_score": beneficiary_score,
                    "amount_score": amount_score,
                    "currency_score": currency_score,
                    "date_score": date_score,
                }
            )

        scored.sort(
            key=lambda item: item[
                "match_score"
            ],
            reverse=True,
        )

        top = scored[:max(1, int(limit))]

        with self.db.transaction() as conn:

            conn.execute(
                """
                DELETE FROM lc_po_matches
                WHERE lc_id = ?
                  AND is_selected = 0
                """,
                (lc_id,),
            )

            for rank, candidate in enumerate(
                top,
                start=1,
            ):
                conn.execute(
                    """
                    INSERT INTO lc_po_matches (
                        lc_id,
                        po_id,
                        match_score,
                        applicant_score,
                        beneficiary_score,
                        amount_score,
                        currency_score,
                        date_score,
                        candidate_rank,
                        match_status,
                        is_selected,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                            'SUGGESTED',
                            0,
                            CURRENT_TIMESTAMP,
                            CURRENT_TIMESTAMP)
                    ON CONFLICT(lc_id, po_id)
                    DO UPDATE SET
                        match_score =
                            excluded.match_score,
                        applicant_score =
                            excluded.applicant_score,
                        beneficiary_score =
                            excluded.beneficiary_score,
                        amount_score =
                            excluded.amount_score,
                        currency_score =
                            excluded.currency_score,
                        date_score =
                            excluded.date_score,
                        candidate_rank =
                            excluded.candidate_rank,
                        updated_at =
                            CURRENT_TIMESTAMP
                    """,
                    (
                        lc_id,
                        candidate["po_id"],
                        candidate["match_score"],
                        candidate[
                            "applicant_score"
                        ],
                        candidate[
                            "beneficiary_score"
                        ],
                        candidate[
                            "amount_score"
                        ],
                        candidate[
                            "currency_score"
                        ],
                        candidate[
                            "date_score"
                        ],
                        rank,
                    ),
                )

        return top

    def select_match(
        self,
        lc_id: int,
        po_id: int,
        performed_by="SYSTEM",
    ) -> dict:

        workflow = self.workflow.get_workflow(
            lc_id
        )

        if workflow is None:
            raise WorkflowNotFoundError(
                f"No workflow for LC id {lc_id}."
            )

        if (
            int(workflow["current_stage"])
            != int(LCStage.PO_MATCHING)
        ):
            raise POMatchingError(
                "LC is not currently in "
                "PO Matching stage."
            )

        match = self.db.fetchone(
            """
            SELECT *
            FROM lc_po_matches
            WHERE lc_id = ?
              AND po_id = ?
            """,
            (
                lc_id,
                po_id,
            ),
        )

        if match is None:
            raise PurchaseOrderNotFoundError(
                "PO is not a candidate "
                "for this LC."
            )

        with self.db.transaction() as conn:

            conn.execute(
                """
                UPDATE lc_po_matches
                SET
                    is_selected = 0,
                    match_status = 'SUGGESTED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE lc_id = ?
                """,
                (lc_id,),
            )

            conn.execute(
                """
                UPDATE lc_po_matches
                SET
                    is_selected = 1,
                    match_status = 'SELECTED',
                    updated_at = CURRENT_TIMESTAMP
                WHERE lc_id = ?
                  AND po_id = ?
                """,
                (
                    lc_id,
                    po_id,
                ),
            )

        self.workflow.record_stage_event(
            lc_id,
            LCStage.PO_MATCHING,
            StageStatus.COMPLETED,
            action="PO_MATCH_SELECTED",
            notes=(
                f"PO id {po_id} selected "
                f"with score "
                f"{float(match['match_score']):.2f}"
            ),
            performed_by=performed_by,
        )

        self.workflow.transition_stage(
            lc_id,
            LCStage.SCRUTINY,
            action="PO_MATCHING_TO_SCRUTINY",
            notes=(
                "Selected PO accepted. "
                "LC moved to Stage 3 Scrutiny."
            ),
            performed_by=performed_by,
        )

        result = self.db.fetchone(
            """
            SELECT
                m.*,
                p.po_number
            FROM lc_po_matches AS m
            JOIN purchase_orders AS p
                ON p.id = m.po_id
            WHERE m.lc_id = ?
              AND m.po_id = ?
            """,
            (
                lc_id,
                po_id,
            ),
        )

        return dict(result)
