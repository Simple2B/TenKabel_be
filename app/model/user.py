from typing import Self
import sqlalchemy as sa
from sqlalchemy import orm, select
from app.hash_utils import hash_verify

from app.database import db, get_db
from .user_profession import users_professions
from .base_user import BaseUser
from .profession import Profession
from app import model as m
from app import schema as s


class User(db.Model, BaseUser):
    __tablename__ = "users"

    phone: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=False, unique=True
    )
    first_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    last_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    professions: orm.Mapped[Profession] = orm.relationship(
        "Profession", secondary=users_professions, viewonly=True
    )
    jobs_count: orm.Mapped[int] = orm.mapped_column(sa.Integer, default=0)

    @classmethod
    def authenticate_with_phone(
        cls, db: orm.Session, user_id: str, password: str
    ) -> Self:
        user = (
            db.query(cls)
            .filter(
                sa.or_(
                    sa.func.lower(cls.phone) == sa.func.lower(user_id),
                    sa.func.lower(cls.email) == sa.func.lower(user_id),
                )
            )
            .first()
        )
        if user is not None and hash_verify(password, user.password):
            return user

    @property
    def jobs_count(self) -> int:
        db = get_db().__next__()

        jobs_list: s.ListJob = db.scalars(
            select(m.Job).where(m.Job.owner_id == self.id)
        ).all()

        return len(jobs_list)

    def __repr__(self):
        return f"<{self.id}: {self.first_name} {self.last_name}>"
