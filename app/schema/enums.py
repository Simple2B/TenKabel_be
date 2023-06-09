import enum
from app.utility.enum_mixin import IndexableStringEnum


class JobStatus(IndexableStringEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    JOB_IS_FINISHED = "JOB_IS_FINISHED"


class NotificationType(IndexableStringEnum):
    JOB_CREATED = "JOB_CREATED"
    JOB_STARTED = "JOB_STARTED"
    JOB_DONE = "JOB_DONE"
    JOB_CANCELED = "JOB_CANCELED"
    JOB_PAID = "JOB_PAID"
    COMMISSION_REQUESTED = "COMMISSION_REQUESTED"
    COMMISSION_PAID = "COMMISSION_PAID"

    MAX_JOB_TYPE = "MAX_JOB_TYPE"

    APPLICATION_CREATED = "APPLICATION_CREATED"
    APPLICATION_ACCEPTED = "APPLICATION_ACCEPTED"
    APPLICATION_REJECTED = "APPLICATION_REJECTED"

    MAX_APPLICATION_TYPE = "MAX_APPLICATION_TYPE"


# Job
class PaymentStatus(enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"


class CommissionStatus(enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    REQUESTED = "requested"


# Payplus
class PlatformPaymentStatus(enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    REJECTED = "REJECTED"
    PROGRESS = "PROGRESS"
