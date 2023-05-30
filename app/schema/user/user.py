from pydantic import BaseModel, EmailStr, AnyHttpUrl, constr
from datetime import datetime

from app.schema.profession import Profession


class AuthUser(BaseModel):
    phone: constr(max_length=128, strip_whitespace=True)
    password: constr(max_length=128, strip_whitespace=True)


class UserSignUp(AuthUser):
    first_name: str
    last_name: str


class GoogleAuthUser(BaseModel):
    email: str
    photo_url: AnyHttpUrl | None
    uid: str | None
    display_name: str | None


class BaseUser(BaseModel):
    email: EmailStr | None
    username: str
    first_name: str
    last_name: str


class User(BaseUser):
    id: int
    uuid: str
    phone: str | None
    jobs_posted_count: int
    jobs_completed_count: int
    positive_rates_count: int
    negative_rates_count: int
    neutral_rates_count: int
    created_at: datetime | str
    is_verified: bool
    professions: list[Profession]
    picture: AnyHttpUrl | None

    class Config:
        orm_mode = True


class UserUpdate(BaseUser):
    email: EmailStr | None
    professions: list[Profession]
    picture: AnyHttpUrl | None
