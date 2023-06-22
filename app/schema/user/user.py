from datetime import datetime
import enum

from pydantic import BaseModel, AnyHttpUrl, constr

from app.schema.profession import Profession
from app.schema.location import Location

phone_field = constr(
    max_length=128,
    strip_whitespace=True,
    regex=r"[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{5,7}$",
)


class AuthUser(BaseModel):
    country_code: str
    phone: phone_field
    password: constr(max_length=128, strip_whitespace=True)


class UserSignUp(AuthUser):
    first_name: str
    last_name: str
    profession_id: int | None
    locations: list[int] | None
    country_code: str


class GoogleAuthUser(BaseModel):
    email: str
    photo_url: AnyHttpUrl | None
    uid: str | None
    display_name: str | None


class BaseUser(BaseModel):
    email: str | None
    username: str
    first_name: str
    last_name: str


class User(BaseUser):
    id: int
    uuid: str
    phone: str | None
    jobs_posted_count: int
    jobs_completed_count: int
    positive_rates_count: int = 0
    negative_rates_count: int = 0
    neutral_rates_count: int = 0
    created_at: datetime | str
    country_code: str
    is_verified: bool
    professions: list[Profession]
    picture: str
    locations: list[Location]
    is_auth_by_google: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseUser):
    professions: list[int] | None
    locations: list[int] | None
    picture: str | None
    phone: phone_field | None
    country_code: str | None


class ForgotPassword(BaseModel):
    new_password: str
    phone: phone_field
    country_code: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


class PasswordStatus(BaseModel):
    class PasswordStatusEnum(enum.Enum):
        OK = "OK"
        PASSWORD_MATCH = "Password match"
        PASSWORD_UPDATED = "Password updated"

    status: PasswordStatusEnum
