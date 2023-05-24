from pydantic import BaseModel, EmailStr, AnyHttpUrl
from datetime import datetime


class BaseUser(BaseModel):
    username: str
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
    created_at: datetime | str

    class Config:
        orm_mode = True
