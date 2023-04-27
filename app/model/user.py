from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database import Base
from .base_user import BaseUser


class User(Base, BaseUser):
    __tablename__ = "users"

    phone = Column(String(128), nullable=False, unique=True)
    first_name = Column(String(64), default="")
    last_name = Column(String(64), default="")
    professions = relationship(
        "Profession", secondary="users_professions", viewonly=True
    )
