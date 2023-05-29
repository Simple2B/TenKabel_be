from typing import Self
import sqlalchemy as sa
from sqlalchemy import orm, select, func
from app.hash_utils import hash_verify

from app.database import db
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
    def jobs_posted_count(self) -> int:
        with db.begin() as session:
            return session.scalar(select(func.count()).where(m.Job.owner_id == self.id))

    @property
    def jobs_completed_count(self) -> int:
        with db.begin() as session:
            return session.scalar(
                select(func.count()).where(
                    (m.Job.worker_id == self.id)
                    & (m.Job.status in (s.Job.Status.COMPLETED, s.Job.Status.FULFILLED))
                )
            )

    @property
    def positive_rates_count(self) -> int:
        with db.begin() as session:
            return session.scalar(
                select(func.count()).where(
                    (m.Rate.worker_id == self.id)
                    & (m.Rate.rate == s.BaseRate.RateStatus.POSITIVE)
                )
            )

    @property
    def negative_rates_count(self) -> int:
        with db.begin() as session:
            return session.scalar(
                select(func.count()).where(
                    (m.Rate.worker_id == self.id)
                    & (m.Rate.rate == s.BaseRate.RateStatus.NEGATIVE)
                )
            )

    @property
    def neutral_rates_count(self) -> int:
        with db.begin() as session:
            return session.scalar(
                select(func.count()).where(
                    (m.Rate.worker_id == self.id)
                    & (m.Rate.rate == s.BaseRate.RateStatus.NEUTRAL)
                )
            )

    def __repr__(self):
        return f"<{self.id}: {self.first_name} {self.last_name}>"
