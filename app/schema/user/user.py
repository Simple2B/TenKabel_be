from pydantic import BaseModel, EmailStr, AnyHttpUrl
from datetime import datetime
from schema.rate import RateList


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
    rates: RateList

    class Config:
        orm_mode = True
