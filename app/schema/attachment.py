import pytz
from datetime import datetime

from pydantic import BaseModel, validator

from .file import FileOut


class AttachmentIn(BaseModel):
    file_uuids: list[str]
    job_id: int


class AttachmentOut(BaseModel):
    uuid: str
    job_id: int
    user_id: int
    file_id: int
    file: FileOut
    created_at: datetime

    @validator("created_at", each_item=True)
    def to_israel_tz(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            value = pytz.utc.localize(value)
        israel_tz = pytz.timezone("Asia/Jerusalem")
        return value.astimezone(israel_tz)

    class Config:
        orm_mode = True
        use_enum_values = True
