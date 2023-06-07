import enum
from pydantic import BaseModel

from .user import User
from .profession import Profession
from .application import Application


class BaseJob(BaseModel):
    uuid: str
    owner_id: int
    worker_id: int | None
    profession_id: int | None
    profession: Profession | None
    name: str
    description: str

    class Config:
        # use_enum_values = True
        orm_mode = True


class Job(BaseJob):
    class Status(enum.Enum):
        PENDING = "pending"
        APPROVED = "approved"
        IN_PROGRESS = "in_progress"
        JOB_IS_FINISHED = "job_is_finished"

    class PaymentStatus(enum.Enum):
        PAID = "paid"
        UNPAID = "unpaid"

    class CommissionStatus(enum.Enum):
        PAID = "paid"
        UNPAID = "unpaid"

    class WhoPays(enum.Enum):
        ME = "me"
        CLIENT = "client"

    class TabFilter(enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"
        ARCHIVE = "archive"

    id: str | None
    status: Status | str
    payment_status: PaymentStatus | str
    commission_status: CommissionStatus | str
    who_pays: WhoPays | str
    is_deleted: bool
    owner: User
    worker: User | None
    payment: int | None
    commission: int | None
    customer_first_name: str | None
    customer_last_name: str | None
    customer_phone: str | None
    customer_street_address: str | None
    city: str
    time: str
    applications: list[Application]

    class Config:
        use_enum_values = True
        orm_mode = True


class ListJob(BaseModel):
    jobs: list[Job]


class JobIn(BaseModel):
    profession_id: int
    city: str
    payment: int
    commission: int
    name: str
    description: str
    time: str
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_street_address: str

    class Config:
        orm_mode = True
        use_enum_values = True


class JobUpdate(JobIn):
    status: Job.Status
