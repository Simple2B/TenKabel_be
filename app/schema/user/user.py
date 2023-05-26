from pydantic import BaseModel, EmailStr, AnyHttpUrl
from datetime import datetime

from app.schema.profession import ProfessionList


class BaseUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    google_openid_key: str | None
    picture: AnyHttpUrl | None

    phone: str | None

    class Config:
        orm_mode = True


class User(BaseUser):
    id: int
    uuid: str
    jobs_posted_count: int
    jobs_completed_count: int
    created_at: datetime | str
    is_verified: bool
    professions: ProfessionList | list

    class Config:
        orm_mode = True


class GoogleAuthUser(BaseModel):
    email: str
    photo_url: AnyHttpUrl | None
    uid: str | None
    display_name: str | None
