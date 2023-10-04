from datetime import datetime
import pytz

from pydantic import BaseModel, validator

from .application import ApplicationOut
from .job import Job
from .enums import NotificationType


class NotificationBase(BaseModel):
    type: NotificationType
    id: int
    user_id: int
    uuid: str
    created_at: datetime | str

    @validator("created_at")
    def to_israel_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = pytz.utc.localize(value)
        israel_tz = pytz.timezone("Asia/Jerusalem")
        return value.astimezone(israel_tz)


class NotificationJob(NotificationBase):
    payload: Job

    class Config:
        orm_mode = True


class NotificationApplication(NotificationBase):
    payload: ApplicationOut

    class Config:
        orm_mode = True


class NotificationList(BaseModel):
    items: list[NotificationJob | NotificationApplication]
