import enum
from pydantic import BaseModel
from .application import ApplicationOut

from .job import Job


class NotificationType(enum.IntEnum):
    JOB_CREATED = 1
    JOB_STARTED = 2
    JOB_DONE = 3
    JOB_CANCELED = 4
    JOB_PAID = 5
    COMMISSION_PAID = 6

    MAX_JOB_TYPE = 10

    APPLICATION_CREATED = 11
    APPLICATION_ACCEPTED = 12
    APPLICATION_REJECTED = 13

    MAX_APPLICATION_TYPE = 20


class NotificationBase(BaseModel):
    type: NotificationType
    id: int
    user_id: int
    uuid: str


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