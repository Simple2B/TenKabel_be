from pydantic import BaseModel

from .enums import NotificationType


class PushNotificationPayload(BaseModel):
    notification_type: NotificationType
    job_uuid: str


class PushNotificationMessage(BaseModel):
    payload: PushNotificationPayload
    device_tokens: list[str] | None
