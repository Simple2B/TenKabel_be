import enum
import pytz
from datetime import datetime

from pydantic import BaseModel, validator
from .user import User
from .enums import JobStatus


class BaseApplication(BaseModel):
    class ApplicationStatus(enum.Enum):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"

    owner_id: int
    worker_id: int
    job_id: int
    status: ApplicationStatus = ApplicationStatus.PENDING

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationPatch(BaseModel):
    owner_id: int | None
    worker_id: int | None
    job_id: int | None
    status: BaseApplication.ApplicationStatus | None

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationIn(BaseModel):
    job_id: int

    class Config:
        use_enum_values = True
        orm_mode = True


class Application(BaseApplication):
    id: int
    uuid: str
    owner: User
    worker: User
    created_at: datetime | str
    status_changed_at: datetime | str

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationOut(Application):
    job_uuid: str
    job_name: str
    job_status: JobStatus

    @validator("created_at", "status_changed_at", each_item=True)
    def created_at_to_israel_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = pytz.utc.localize(value)
        israel_tz = pytz.timezone("Asia/Jerusalem")
        return value.astimezone(israel_tz)


class ApplicationList(BaseModel):
    applications: list[ApplicationOut]

    class Config:
        orm_mode = True
