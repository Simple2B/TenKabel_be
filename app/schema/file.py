from datetime import datetime

from pydantic import BaseModel

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

    class Config:
        orm_mode = True
        use_enum_values = True
