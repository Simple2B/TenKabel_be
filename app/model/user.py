from sqlalchemy import Column, String

from app.database import Base
from .base_user import BaseUser


class User(Base, BaseUser):
    google_openid = Column(String(64), default="")
    otp_code = Column(String(16), default="")

    __tablename__ = "users"
