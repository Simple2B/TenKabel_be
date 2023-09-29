import enum
from datetime import datetime

from pydantic import BaseModel

from .user import User, UserPicture
from .profession import Profession
from .application import ApplicationOut
from .enums import JobStatus as Status, PaymentStatus, CommissionStatus
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
    status: Status
    payment_status: PaymentStatus
    commission_status: CommissionStatus
    platform_commissions: list[PlatformCommission]
    who_pays: WhoPays
    is_deleted: bool
    owner: User
    is_asap: bool
    frame_time: str | None
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

    pending_at: datetime | None
    approved_at: datetime | None
    in_progress_at: datetime | None
    job_is_finished_at: datetime | None

    attachments: list[AttachmentOut] | None

    class Config:
        orm_mode = True
        use_enum_values = True


class SearchJob(BaseJob):
    class WhoPays(enum.Enum):
        ME = "me"
        CLIENT = "client"

    class TabFilter(enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"
        ARCHIVE = "archive"

    id: int
    uuid: str
    status: Status
    payment_status: PaymentStatus
    commission_status: CommissionStatus
    is_deleted: bool
    regions: list[Location]
    owner: UserPicture
    is_asap: bool
    frame_time: str | None

    payment: int | None
    commission: int | None
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_street_address: str
    city: str
    time: str
    owner_rate_uuid: str | None
    worker_rate_uuid: str | None

    class Config:
        orm_mode = True
        use_enum_values = True


class ListJobSearch(BaseModel):
    jobs: list[SearchJob]


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
    is_asap: bool
    frame_time: str | None = None
    time: str
    customer_first_name: str
    customer_last_name: str
    customer_phone: str
    customer_street_address: str

    file_uuids: list[str] = []

    class Config:
        orm_mode = True
        use_enum_values = True


class JobUpdate(JobIn):
    status: Status
    payment_status: PaymentStatus
    commission_status: CommissionStatus


class JobPatch(BaseModel):
    profession_id: int | None
    regions: list[int] | None
    city: str | None
    payment: int | None
    commission: int | None
    payment_status: PaymentStatus | None
    is_asap: bool | None
    commission_status: CommissionStatus | None
    frame_time: str | None
    name: str | None
    description: str | None
    time: str | None
    customer_first_name: str | None
    customer_last_name: str | None
    customer_phone: str | None
    customer_street_address: str | None
    status: Status | None
    file_uuids: list[str] = []

    class Config:
        orm_mode = True
        use_enum_values = True


class Payment(BaseModel):
    id: int
    job_id: int
    uuid: str
    payment_status: PaymentStatus
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class PaymentList(BaseModel):
    payments: list[Payment]


class Commission(BaseModel):
    id: int
    job_id: int
    uuid: str
    commission_status: CommissionStatus
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class CommissionList(BaseModel):
    commissions: list[Commission]


class JobStatus(BaseModel):
    id: int
    job_id: int
    uuid: str
    status: Status
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class JobStatusList(BaseModel):
    statuses: list[JobStatus]
