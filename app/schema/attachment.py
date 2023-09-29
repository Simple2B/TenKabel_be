from datetime import datetime

from pydantic import BaseModel

from .file import FileOut


class AttachmentIn(BaseModel):
    file_uuids: list[str]
    job_id: int


class AttachmentOut(BaseModel):
    uuid: str
    job_id: int
    user_id: int
    file_id: int | None
    file: FileOut | None
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
