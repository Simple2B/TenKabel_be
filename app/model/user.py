from typing import Self
import sqlalchemy as sa
from sqlalchemy import orm, select, func
from app.hash_utils import hash_verify

from app.database import db
from .user_profession import users_professions
from .user_location import users_locations
from .base_user import BaseUser
from .profession import Profession
from .location import Location
from app import schema as s
from app import model as m


class User(db.Model, BaseUser):
    __tablename__ = "users"

    phone: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=True, unique=True
    )
    first_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    last_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    professions: orm.Mapped[Profession] = orm.relationship(
        "Profession", secondary=users_professions, viewonly=True
    )
    locations: orm.Mapped[Location] = orm.relationship(
        "Location", secondary=users_locations, viewonly=True
    )

    @classmethod
    def authenticate_with_phone(
        cls,
        db: orm.Session,
        user_id: str,
        password: str,
        country_code: str | None = None,
    ) -> Self:
        if country_code:
            filters = sa.and_(
                sa.func.lower(cls.phone) == sa.func.lower(user_id),
                sa.func.lower(cls.country_code) == sa.func.lower(country_code),
            )
        else:
            filters = sa.and_(
                sa.func.lower(cls.phone) == sa.func.lower(user_id),
            )
        user = (
            db.query(cls)
            .filter(
                sa.or_(
                    filters,
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
                    & (m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED)
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
