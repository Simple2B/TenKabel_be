from typing import Self, TYPE_CHECKING
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy import orm

from app.hash_utils import hash_verify
from app.database import db
from app import schema as s
from app.logger import log
from app.config import get_settings, Settings

from .user_profession import users_professions
from .user_location import users_locations
from .user_notifications_professions import users_notifications_professions
from .user_notifications_location import users_notifications_locations
from .base_user import BaseUser


if TYPE_CHECKING:
    from .profession import Profession
    from .location import Location
    from .attachment import Attachment
    from .applications import Application


class User(db.Model, BaseUser):
    __tablename__ = "users"

    phone: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=True, unique=True
    )
    first_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    last_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")

    professions: orm.Mapped[list["Profession"]] = orm.relationship(
        "Profession", secondary=users_professions, viewonly=True
    )
    locations: orm.Mapped[list["Location"]] = orm.relationship(
        "Location", secondary=users_locations, viewonly=True
    )

    notification_profession_flag: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean, default=True
    )
    notification_professions: orm.Mapped[list["Profession"]] = orm.relationship(
        "Profession", secondary=users_notifications_professions, viewonly=True
    )

    notification_locations_flag: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean, default=True
    )
    notification_locations: orm.Mapped[list["Location"]] = orm.relationship(
        "Location", secondary=users_notifications_locations, viewonly=True
    )

    notification_job_status: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean, default=True
    )

    payplus_customer_uid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        nullable=True,
    )

    payplus_card_uid: orm.Mapped[str] = orm.mapped_column(
        sa.String(64), nullable=True, unique=True
    )

    card_name: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=True)
    attachments: orm.Mapped["Attachment"] = orm.relationship(
        "Attachment",
        backref="user",
    )

    applications: orm.WriteOnlyMapped["Application"] = orm.relationship(
        foreign_keys="Application.owner_id",
        passive_deletes=True,
    )

    files: orm.Mapped["File"] = orm.relationship(  # noqa: F821
        "File",
        backref="user",
    )

    @property
    def is_payment_method_invalid(self) -> bool:
        return any(
            [
                pp.status == s.enums.PlatformPaymentStatus.REJECTED
                for pp in self.platform_payments
            ]
        )

    @classmethod
    def authenticate_with_phone(
        cls,
        db: orm.Session,
        user_id: str,
        password: str,
        country_code: str,
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

        if user and user.is_deleted:
            log(log.INFO, "User is deleted")
            return None

        if user is not None and hash_verify(password, user.password):
            return user

    @property
    def jobs_posted_count(self) -> int:
        return len(self.jobs_owned)

    @property
    def jobs_completed_count(self) -> int:
        return sum(
            [job.status == s.enums.JobStatus.JOB_IS_FINISHED for job in self.jobs_to_do]
        )

    @property
    def jobs_canceled_count(self) -> int:
        return sum([job.is_deleted for job in self.jobs_to_do])

    @property
    def positive_rates_count(self) -> int:
        return sum(
            [rate.rate == s.BaseRate.RateStatus.POSITIVE for rate in self.owned_rates]
        )

    @property
    def negative_rates_count(self) -> int:
        return sum(
            [rate.rate == s.BaseRate.RateStatus.NEGATIVE for rate in self.owned_rates]
        )

    @property
    def neutral_rates_count(self) -> int:
        return sum(
            [rate.rate == s.BaseRate.RateStatus.NEUTRAL for rate in self.owned_rates]
        )

    @property
    def is_new_user(self) -> bool:
        settings: Settings = get_settings()
        # check how many days ago user was created
        if (
            datetime.now() - timedelta(days=settings.NEW_USER_TERM_DAYS)
            < self.created_at
        ):
            return True
        return False

    def __repr__(self):
        if self.first_name and self.last_name:
            return f"<{self.id}: {self.first_name} {self.last_name}>"
        return f"<{self.id}: {self.email}>"
