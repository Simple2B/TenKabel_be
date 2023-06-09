import enum
from datetime import datetime

from pydantic import BaseModel


class BaseApplication(BaseModel):
    class ApplicationStatus(enum.Enum):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"

    owner_id: int
    worker_id: int
    job_id: int
    status: ApplicationStatus | str = ApplicationStatus.PENDING

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
    worker_uuid: str
    owner_uuid: str
    created_at: datetime | str
    status_changed_at: datetime | str

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationList(BaseModel):
    applications: list[Application]
