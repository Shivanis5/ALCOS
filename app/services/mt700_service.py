from __future__ import annotations

from app.core.database import DatabaseManager


class MT700Service:
    """
    Handles MT700 database operations.
    """

    def __init__(self):

        self.db = DatabaseManager()

    ####################################################
    # Save MT700
    ####################################################

    def save_mt700(
        self,
        lc_number,
        field_27,
        field_40A,
        field_20,
        field_31C,
        field_31D,
        field_50,
        field_59,
        field_32B,
        field_39A,
        field_41A,
        field_42C,
        field_43P,
        field_43T,
        field_44A,
        field_44B,
        field_44C,
        field_44E,
        field_44F,
        field_45A,
        field_46A,
        field_47A,
        field_71B,
        field_48,
        field_49,
        field_57A,
        field_78,
        field_72,
    ):

        query = """
        INSERT INTO mt700
        (
            lc_number,
            field_27,
            field_40A,
            field_20,
            field_31C,
            field_31D,
            field_50,
            field_59,
            field_32B,
            field_39A,
            field_41A,
            field_42C,
            field_43P,
            field_43T,
            field_44A,
            field_44B,
            field_44C,
            field_44E,
            field_44F,
            field_45A,
            field_46A,
            field_47A,
            field_71B,
            field_48,
            field_49,
            field_57A,
            field_78,
            field_72
        )
        VALUES
        (
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?
        )
        """

        self.db.execute(
            query,
            (
                lc_number,
                field_27,
                field_40A,
                field_20,
                field_31C,
                field_31D,
                field_50,
                field_59,
                field_32B,
                field_39A,
                field_41A,
                field_42C,
                field_43P,
                field_43T,
                field_44A,
                field_44B,
                field_44C,
                field_44E,
                field_44F,
                field_45A,
                field_46A,
                field_47A,
                field_71B,
                field_48,
                field_49,
                field_57A,
                field_78,
                field_72,
            ),
        )

    ####################################################
    # Load MT700
    ####################################################

    def load_mt700(self, lc_number):

        query = """
        SELECT *
        FROM mt700
        WHERE lc_number=?
        """

        return self.db.fetchone(
            query,
            (
                lc_number,
            ),
        )