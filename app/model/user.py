from app.database import Base
from .base_user import BaseUser


class User(Base, BaseUser):
    __tablename__ = "users"
