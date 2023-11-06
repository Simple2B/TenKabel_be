from datetime import datetime
import pytz

from pydantic import BaseModel, validator

from .enums import AttachmentType


class BaseFile(BaseModel):
    filename: str


class FileOut(BaseFile):
    uuid: str
    original_filename: str
    extension: str
    url: str
    type: AttachmentType
    created_at: datetime | None

    @validator("created_at")
    def created_at_to_israel_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = pytz.utc.localize(value)
        israel_tz = pytz.timezone("Asia/Jerusalem")
        return value.astimezone(israel_tz)

    class Config:
        orm_mode = True
        use_enum_values = True
