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
    COMMISSION_DENIED = "COMMISSION_DENIED"
    COMMISSION_SENT = "COMMISSION_SENT"

    PAYMENT_REQUESTED = "PAYMENT_REQUESTED"
    PAYMENT_SENT = "PAYMENT_SENT"
    PAYMENT_DENIED = "PAYMENT_DENIED"

    MAX_JOB_TYPE = "MAX_JOB_TYPE"

    APPLICATION_CREATED = "APPLICATION_CREATED"
    APPLICATION_ACCEPTED = "APPLICATION_ACCEPTED"
    APPLICATION_REJECTED = "APPLICATION_REJECTED"

    MAX_APPLICATION_TYPE = "MAX_APPLICATION_TYPE"


# Job
class PaymentsTab(enum.Enum):
    PAYMENT = "PAYMENT"
    COMMISSION = "COMMISSION"


class AdditionalInfoTab(enum.Enum):
    UNPAID = "UNPAID"
    APPROVE = "APPROVE"
    SEND = "SEND"


class PaymentStatus(IndexableStringEnum):
    REQUESTED = "REQUESTED"
    SENT = "SENT"
    UNPAID = "UNPAID"
    DENY = "DENY"
    CONFIRM = "CONFIRM"
    PAID = "PAID"


class PaymentMethod(enum.Enum):
    ADD = "Add"
    UPDATE = "Update"


class CommissionStatus(IndexableStringEnum):
    REQUESTED = "REQUESTED"
    SENT = "SENT"
    CONFIRM = "CONFIRM"
    UNPAID = "UNPAID"
    DENY = "DENY"
    PAID = "PAID"


# Payplus
class PlatformPaymentStatus(enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    REJECTED = "REJECTED"
    PROGRESS = "PROGRESS"


class AttachmentType(enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"


class ImageExtension(enum.Enum):
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    SVG = "svg"
    WEBP = "webp"
    TIFF = "tiff"
