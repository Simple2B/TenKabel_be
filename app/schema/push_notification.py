from pydantic import BaseModel, validator

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

    @validator("job_time", pre=True, always=True)
    def format_time(cls, value):
        try:
            # Attempt to format the input to "YYYY-MM-DD HH:MM"
            formatted_time = value.strftime("%Y-%m-%d %H:%M")
            return formatted_time
        except (AttributeError, ValueError):
            # If formatting fails, return the original value
            return value


class PushNotificationMessage(BaseModel):
    payload: PushNotificationPayload
    device_tokens: list[str] | None
