import enum
from pydantic import BaseModel

from .user import User


class BaseJob(BaseModel):
    uuid: str
    owner_id: int
    worker_id: int | None
    profession_id: int | None

    name: str
    description: str

    class Config:
        # use_enum_values = True
        orm_mode = True


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

    uuid: str
    status: Status | str
    payment_status: PaymentStatus | str
    commission_status: CommissionStatus | str
    is_deleted: bool
    owner: User | None
    worker: User | None
    payment: int | None
    commission: int | None
    city: str
    time: str

    class Config:
        use_enum_values = True
        orm_mode = True


class ListJob(BaseModel):
    jobs: list[Job]
