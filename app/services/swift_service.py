from pathlib import Path


class SwiftService:
    """
    Generates SWIFT MT700 message.
    """

    OUTPUT_DIR = Path("generated/mt700")

    def __init__(self):
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_mt700(self, data):

        filename = self.OUTPUT_DIR / f"{data['lc_number']}.txt"

        message = f"""
:27:{data['field27']}
:40A:{data['field40A']}
:20:{data['lc_number']}
:31C:{data['issue_date']}
:31D:{data['expiry_date']}
:50:{data['applicant']}
:59:{data['beneficiary']}
:32B:{data['amount']}
:39A:{data['tolerance']}
:43P:{data['partial']}
:43T:{data['transshipment']}
:44A:{data['receipt']}
:44B:{data['destination']}
:44C:{data['shipment_date']}
:44E:{data['loading']}
:44F:{data['discharge']}
:45A:{data['goods']}
:46A:{data['documents']}
:47A:{data['conditions']}
"""

        filename.write_text(message.strip())

        return filename