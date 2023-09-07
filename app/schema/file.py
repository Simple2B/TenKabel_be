from datetime import datetime

from pydantic import BaseModel

from .enums import AttachmentType


class BaseFile(BaseModel):
    filename: str


class FileIn(BaseFile):
    file: str  # base64 encoded file


class FileOut(BaseFile):
    uuid: str
    filename: str
    original_filename: str
    extension: str
    url: str
    type: AttachmentType
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
