import sqlalchemy as sa
from sqlalchemy import orm

# from sqlalchemy import Column, String
# from sqlalchemy.orm import relationship

from app.database import db
from .user_profession import users_professions
from .base_user import BaseUser


class User(db.Model, BaseUser):
    __tablename__ = "users"

    phone: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=False, unique=True
    )

    # phone = Column(String(128), nullable=False, unique=True)
    first_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")

    # first_name = Column(String(64), default="")

    last_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")

    # last_name = Column(String(64), default="")

    professions: orm.Mapped["Profession"] = orm.relationship(
        "Profession", secondary=users_professions, viewonly=True
    )

    # professions = relationship(
    #     "Profession", secondary="users_professions", viewonly=True
    # )
