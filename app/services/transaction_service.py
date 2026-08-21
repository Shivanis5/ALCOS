from __future__ import annotations

from app.core.database import DatabaseManager
from app.services.lc_workflow_service import create_workflow_for_lc


class TransactionService:
    """
    Handles Trade Transaction database operations.

    Saving an existing LC number updates that LC rather than
    attempting to create a duplicate record.
    """

    def __init__(self):
        self.db = DatabaseManager()

    def create_transaction(
        self,
        transaction_id,
        transaction_reference,
        lc_number,
        applicant,
        beneficiary,
        amount,
        currency,
        status,
        issue_date,
        expiry_date,
    ):
        lc_number = str(lc_number).strip()

        if not lc_number:
            raise ValueError("LC Number is required.")

        applicant = str(applicant or "").strip()
        beneficiary = str(beneficiary or "").strip()
        currency = str(currency or "").strip().upper()
        status = str(status or "").strip()

        with self.db.transaction() as conn:

            existing = conn.execute(
                """
                SELECT id
                FROM letters_of_credit
                WHERE lc_number = ?
                """,
                (lc_number,),
            ).fetchone()

            if existing is None:

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
                        applicant,
                        beneficiary,
                        amount,
                        currency,
                        status,
                        issue_date,
                        expiry_date,
                    ),
                )

                lc_id = int(cursor.lastrowid)
                save_action = "created"

            else:

                lc_id = int(existing["id"])

                conn.execute(
                    """
                    UPDATE letters_of_credit
                    SET
                        applicant = ?,
                        beneficiary = ?,
                        amount = ?,
                        currency = ?,
                        status = ?,
                        issue_date = ?,
                        expiry_date = ?
                    WHERE id = ?
                    """,
                    (
                        applicant,
                        beneficiary,
                        amount,
                        currency,
                        status,
                        issue_date,
                        expiry_date,
                        lc_id,
                    ),
                )

                save_action = "updated"

            # Idempotent: creates the workflow only if one
            # does not already exist for this LC.
            create_workflow_for_lc(
                lc_id,
                connection=conn,
            )

        print(
            f"Transaction {lc_number} "
            f"{save_action} successfully."
        )

        return lc_id
