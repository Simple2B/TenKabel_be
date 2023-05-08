import enum
from pydantic import BaseModel

from .user import User


class BaseJob(BaseModel):
    owner_id: int
    worker_id: int
    profession_id: int

    name: str
    description: str


class Job(BaseJob):
    class Status(enum.Enum):
        PENDING = "pending"
        LATE = "late"
        STARTED = "Started"
        COMPLETED = "Completed"
        FULFILLED = "Fulfilled"

    class PaymentStatus(enum.Enum):
        PAID = "paid"
        UNPAID = "unpaid"

    class CommissionStatus(enum.Enum):
        PAID = "paid"
        UNPAID = "unpaid"

    status: Status
    payment_status: PaymentStatus
    commission_status: CommissionStatus
    is_deleted: bool
    owner: User
    worker: User
