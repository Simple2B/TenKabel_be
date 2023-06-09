from datetime import datetime

from pydantic import BaseModel, EmailStr, AnyHttpUrl, constr

from app.schema.profession import Profession
from app.schema.location import Location

phone_field = constr(
    max_length=128,
    strip_whitespace=True,
    regex=r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$",
)


class AuthUser(BaseModel):
    phone: phone_field
    password: constr(max_length=128, strip_whitespace=True)


class UserSignUp(AuthUser):
    first_name: str
    last_name: str
    profession_id: int | None
    locations: list[int] | None


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
    picture: str | None
    locations: list[Location]
    is_auth_by_google: bool

    # @validator("picture")
    # def encode_picture_to_base64(cls, value) -> bytes:
    #     return value.decode("utf-8")

    class Config:
        orm_mode = True


class UserUpdate(BaseUser):
    professions: list[int]
    picture: str | None
    phone: str | None


class ForgotPassword(BaseModel):
    new_password: str
    phone: phone_field


class ChangePassword(BaseModel):
    current_password: str
    new_password: str
