import enum
from datetime import datetime

from pydantic import BaseModel


class BaseApplication(BaseModel):
    class Status(enum.Enum):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"

    owner_id: int
    worker_id: int
    job_id: int
    status: Status | str = Status.PENDING

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationIn(BaseModel):
    worker_id: int | None

    class Config:
        use_enum_values = True
        orm_mode = True


class Application(BaseApplication):
    id: str
    uuid: str
    created_at: datetime | str

    class Config:
        use_enum_values = True
        orm_mode = True


class ApplicationList(BaseModel):
    applications: list[Application]
