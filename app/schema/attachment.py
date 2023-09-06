from datetime import datetime

from pydantic import BaseModel

from .enums import AttachmentType


class BaseAttachment(BaseModel):
    filename: str


class AttachmentIn(BaseAttachment):
    file: str  # base64 encoded file


class AttachmentOut(BaseAttachment):
    uuid: str
    job_id: int | None
    filename: str
    original_filename: str
    extension: str
    url: str
    type: AttachmentType
    uploaded_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True