from pydantic import BaseModel, EmailStr
from datetime import datetime


class BaseUserGoogle(BaseModel):
    username: str | None
    email: EmailStr
    google_openid: str

    class Config:
        orm_mode = True


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    password: str


class User(BaseModel):
    id: int
    uuid: str

    username: str
    email: EmailStr
    phone_number: str

    first_name: str
    last_name: str

    google_openid: str
    created_at: datetime | str

    class Config:
        orm_mode = True
