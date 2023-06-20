from datetime import datetime

from pydantic import BaseModel

from .application import ApplicationOut
from .job import Job
from .enums import NotificationType


class NotificationBase(BaseModel):
    type: NotificationType
    id: int
    user_id: int
    uuid: str
    created_at: datetime | str


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
