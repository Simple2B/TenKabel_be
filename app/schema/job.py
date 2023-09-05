import enum
from pydantic import BaseModel

from .user import User
from .profession import Profession
from .application import ApplicationOut
from .enums import JobStatus, PaymentStatus, CommissionStatus
from .platform_commission import PlatformCommission
from .attachment import AttachmentOut
from .location import Location


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
    class WhoPays(enum.Enum):
        ME = "me"
        CLIENT = "client"

    class TabFilter(enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"
        ARCHIVE = "archive"

    id: int
    status: JobStatus
    payment_status: PaymentStatus
    commission_status: CommissionStatus
    platform_commissions: list[PlatformCommission]
    who_pays: WhoPays
    is_deleted: bool
    owner: User
    worker: User | None
    payment: int | None
    commission: int | None
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_street_address: str
    regions: list[Location]
    city: str
    time: str
    applications: list[ApplicationOut]
    owner_rate_uuid: str | None
    worker_rate_uuid: str | None

    worker_attachments: list[AttachmentOut]
    owner_attachments: list[AttachmentOut]

    class Config:
        orm_mode = True
        use_enum_values = True


class ListJob(BaseModel):
    jobs: list[Job]


class JobIn(BaseModel):
    profession_id: int
    city: str
    regions: list[int]
    payment: int
    commission: int
    who_pays: Job.WhoPays | None
    name: str
    description: str
    time: str
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_street_address: str

    attachment_uuids: list[str] = []

    class Config:
        orm_mode = True
        use_enum_values = True


class JobUpdate(JobIn):
    status: JobStatus
    payment_status: PaymentStatus
    commission_status: CommissionStatus


class JobPatch(BaseModel):
    profession_id: int | None
    region: str | None
    city: str | None
    payment: int | None
    commission: int | None
    payment_status: PaymentStatus | None
    commission_status: CommissionStatus | None
    name: str | None
    description: str | None
    time: str | None
    customer_first_name: str | None
    customer_last_name: str | None
    customer_phone: str | None
    customer_street_address: str | None
    status: JobStatus | None
    attachment_uuids: list[str] = []

    class Config:
        orm_mode = True
        use_enum_values = True
