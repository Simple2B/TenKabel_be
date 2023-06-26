from pydantic import BaseModel

from .enums import NotificationType


class PushNotificationPayload(BaseModel):
    notification_type: NotificationType
    job_uuid: str
    job_name: str
    job_price: str
    job_time: str
    job_area: str
    job_commission: str
    worker_name: str
    owner_name: str


class PushNotificationMessage(BaseModel):
    payload: PushNotificationPayload
    device_tokens: list[str] | None
