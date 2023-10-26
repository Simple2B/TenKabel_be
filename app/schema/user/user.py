from datetime import datetime
import enum

from pydantic import BaseModel, EmailStr, AnyHttpUrl, constr

from app.schema.profession import Profession
from app.schema.location import Location
from app.config import get_settings
from app.schema.review import ReviewsOut
from app.schema.attachment import AttachmentOut

settings = get_settings()

phone_field = constr(
    max_length=128,
    strip_whitespace=True,
    regex=r"[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{0,7}$",
)


class AuthUser(BaseModel):
    country_code: str = "IL"
    phone: phone_field
    password: constr(max_length=128, strip_whitespace=True)


class UserSignUp(AuthUser):
    first_name: str
    last_name: str
    profession_id: int | None
    locations: list[int] | None
    country_code: str
    email: EmailStr


class GoogleAuthUser(BaseModel):
    email: EmailStr
    first_name: str = ""
    last_name: str = ""
    photo_url: AnyHttpUrl | str | None
    uid: str | None
    display_name: str | None
    country_code: str = "IL"
    phone: phone_field | None
    locations: list[int] | None
    profession_id: int | None


class AppleAuthUser(BaseModel):
    email: EmailStr
    uid: str | None
    display_name: str | None
    country_code: str = "IL"
    phone: phone_field | None
    locations: list[int] | None
    profession_id: int | None


class BaseUser(BaseModel):
    email: str | None
    username: str
    first_name: str
    last_name: str


class UserNotificationSettingsIn(BaseModel):
    notification_profession_flag: bool | None
    notification_profession: list[int] | None
    notification_locations_flag: bool | None
    notification_locations: list[int] | None
    notification_job_status: bool | None


class UserNotificationSettingsOut(BaseModel):
    notification_profession_flag: bool
    notification_profession: list[int]
    notification_locations_flag: bool
    notification_locations: list[int]
    notification_job_status: bool


class ProfileJobInfo(BaseModel):
    uuid: str
    id: int
    attachments: list[AttachmentOut]
    payment: int
    name: str

    class Config:
        orm_mode = True


class UserCollaboration(BaseModel):
    id: int
    uuid: str
    first_name: str
    last_name: str
    picture: str = settings.DEFAULT_AVATAR_PROFILE_URL

    class Config:
        orm_mode = True


class JobsCollaborationsWorkers(ProfileJobInfo):
    worker: UserCollaboration | None

    class Config:
        orm_mode = True


class JobsCollaborationsOwners(ProfileJobInfo):
    owner: UserCollaboration

    class Config:
        orm_mode = True


class User(BaseUser):
    id: int
    uuid: str
    phone: str | None
    jobs_posted_count: int
    jobs_completed_count: int
    jobs_canceled_count: int
    positive_rates_count: int = 0
    negative_rates_count: int = 0
    neutral_rates_count: int = 0
    created_at: datetime | str
    country_code: str
    is_verified: bool
    professions: list[Profession]
    picture: str = settings.DEFAULT_AVATAR_PROFILE_URL
    locations: list[Location]
    is_auth_by_google: bool
    card_name: str | None

    notification_profession_flag: bool
    notification_profession: list[Profession]
    notification_locations_flag: bool
    notification_locations: list[Location]
    notification_job_status: bool

    class Config:
        orm_mode = True


class UserProfile(User):
    owned_rates: list[ReviewsOut]
    given_rates: list[ReviewsOut]

    jobs_owned: list[JobsCollaborationsWorkers]
    jobs_to_do: list[JobsCollaborationsOwners]

    class Config:
        orm_mode = True


class UserPicture(BaseUser):
    id: int
    uuid: str
    picture: str = settings.DEFAULT_AVATAR_PROFILE_URL

    class Config:
        orm_mode = True


class UserUpdate(BaseUser):
    professions: list[int] | None
    locations: list[int] | None
    picture: str | None
    phone: phone_field | None
    country_code: str | None


class UserUpdateIn(BaseUser):
    professions: list[int] | None
    locations: list[int] | None
    picture: str | None
    picture_filename: str | None
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


class UserExists(BaseModel):
    exists: bool
