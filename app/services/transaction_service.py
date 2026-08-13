from __future__ import annotations

from app.core.database import DatabaseManager


class TransactionService:
    """
    Handles Trade Transaction database operations.
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

        query = """
        INSERT INTO letters_of_credit
        (
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
        """

        self.db.execute(
            query,
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

        self.db.commit()

        print(f"Transaction {lc_number} saved successfully.")