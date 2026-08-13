from enum import Enum, IntEnum


class LCStage(IntEnum):
    """
    ALCOS LC processing stages.

    Dashboard & Assistant is intentionally not included here because
    it monitors the whole lifecycle rather than being a processing
    stage that an LC must pass through.
    """

    INTAKE = 1
    PO_MATCHING = 2
    SCRUTINY = 3
    AMENDMENT = 4
    DOCUMENTS = 5
    BANK_SUBMISSION = 6
    DISCOUNTING = 7
    PAYMENT_TRACKING = 8


class StageStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_HUMAN = "WAITING_HUMAN"
    WAITING_EXTERNAL = "WAITING_EXTERNAL"
    PASSED = "PASSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    NOT_REQUIRED = "NOT_REQUIRED"


class LCStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


STAGE_LABELS = {
    LCStage.INTAKE: "LC Intake",
    LCStage.PO_MATCHING: "PO Matching",
    LCStage.SCRUTINY: "Scrutiny",
    LCStage.AMENDMENT: "Amendments",
    LCStage.DOCUMENTS: "Document Preparation",
    LCStage.BANK_SUBMISSION: "Bank Submission",
    LCStage.DISCOUNTING: "Discounting",
    LCStage.PAYMENT_TRACKING: "Payment Tracking",
}


ALLOWED_TRANSITIONS = {
    LCStage.INTAKE: {
        LCStage.PO_MATCHING,
    },

    LCStage.PO_MATCHING: {
        LCStage.SCRUTINY,
    },

    # Scrutiny can either proceed normally or open an amendment cycle.
    LCStage.SCRUTINY: {
        LCStage.AMENDMENT,
        LCStage.DOCUMENTS,
    },

    # An amended LC MUST return to scrutiny.
    LCStage.AMENDMENT: {
        LCStage.SCRUTINY,
    },

    LCStage.DOCUMENTS: {
        LCStage.BANK_SUBMISSION,
    },

    LCStage.BANK_SUBMISSION: {
        LCStage.DISCOUNTING,
    },

    LCStage.DISCOUNTING: {
        LCStage.PAYMENT_TRACKING,
    },

    LCStage.PAYMENT_TRACKING: set(),
}


DASHBOARD_STEP = 9
DASHBOARD_LABEL = "Dashboard & Assistant"


def stage_label(stage):
    """Return the human-readable label for a stage."""
    return STAGE_LABELS[LCStage(stage)]


def can_transition(current_stage, next_stage):
    """Check whether one workflow transition is allowed."""
    current = LCStage(current_stage)
    target = LCStage(next_stage)

    return target in ALLOWED_TRANSITIONS[current]


def next_normal_stage(current_stage):
    """
    Return the normal forward stage.

    Scrutiny normally proceeds to Documents.
    Amendment is special and returns to Scrutiny.
    """

    current = LCStage(current_stage)

    normal_flow = {
        LCStage.INTAKE: LCStage.PO_MATCHING,
        LCStage.PO_MATCHING: LCStage.SCRUTINY,
        LCStage.SCRUTINY: LCStage.DOCUMENTS,
        LCStage.AMENDMENT: LCStage.SCRUTINY,
        LCStage.DOCUMENTS: LCStage.BANK_SUBMISSION,
        LCStage.BANK_SUBMISSION: LCStage.DISCOUNTING,
        LCStage.DISCOUNTING: LCStage.PAYMENT_TRACKING,
        LCStage.PAYMENT_TRACKING: None,
    }

    return normal_flow[current]
