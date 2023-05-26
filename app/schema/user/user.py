from pydantic import BaseModel, EmailStr, AnyHttpUrl
from datetime import datetime


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

    class Config:
        orm_mode = True
