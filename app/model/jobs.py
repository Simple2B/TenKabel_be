from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.exceptions import ValueDownGradeForbidden
from app.utility import generate_uuid
from app import schema as s
from app import model as m
from app.model.applications import Application
from .platform_comission import PlatformCommission


class Job(db.Model):
    __tablename__ = "jobs"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

    owner_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    worker_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=True
    )

    profession_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("professions.id"), nullable=True
    )

    name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    description: orm.Mapped[str] = orm.mapped_column(sa.String(512), default="")
    is_deleted: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)
    status: orm.Mapped[s.enums.JobStatus] = orm.mapped_column(
        sa.Enum(s.enums.JobStatus), default=s.enums.JobStatus.PENDING
    )

    customer_first_name: orm.Mapped[str] = orm.mapped_column(
        sa.String(64), nullable=False
    )
    customer_last_name: orm.Mapped[str] = orm.mapped_column(
        sa.String(64), nullable=False
    )
    customer_phone: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)
    customer_street_address: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=False
    )

    payment: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)
    commission: orm.Mapped[float] = orm.mapped_column(sa.Float, nullable=False)

    city: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)
    formatted_time: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)

    payment_status: orm.Mapped[s.enums.PaymentStatus] = orm.mapped_column(
        sa.Enum(s.enums.PaymentStatus), default=s.enums.PaymentStatus.UNPAID
    )
    commission_status: orm.Mapped[s.enums.CommissionStatus] = orm.mapped_column(
        sa.Enum(s.enums.CommissionStatus), default=s.enums.CommissionStatus.UNPAID
    )

    who_pays: orm.Mapped[s.Job.WhoPays] = orm.mapped_column(
        sa.Enum(s.Job.WhoPays), default=s.Job.WhoPays.ME
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )

    # relationships
    applications: orm.Mapped[list[Application]] = orm.relationship(
        "Application", viewonly=True, backref="job"
    )
    worker: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[worker_id], viewonly=True, backref="jobs_to_do"
    )
    owner: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[owner_id], viewonly=True, backref="jobs_owned"
    )
    platform_commissions: orm.Mapped[PlatformCommission] = orm.relationship(
        "PlatformCommission", backref="job"
    )

    profession: orm.Mapped[m.Profession] = orm.relationship("Profession", viewonly=True)

    @property
    def owner_rate_uuid(self) -> str | None:
        rates = [rate for rate in self.rates if rate.worker_id == self.owner_id]
        # rate = self.rates.filter_by(worker_id=self.owner_id).first()
        return rates[0].uuid if rates else None

    @property
    def worker_rate_uuid(self) -> str | None:
        rates = [rate for rate in self.rates if rate.worker_id == self.worker_id]
        return rates[0].uuid if rates else None

    # @property
    # def rated_by_owner(self) -> bool:
    #     return self.owner_id in [rate.worker_id for rate in self.rates]

    # @property
    # def rated_by_worker(self) -> bool:
    #     return self.worker_id in [rate.worker_id for rate in self.rates]

    @property
    def time(self) -> str:
        return self.formatted_time

    @time.setter
    def time(self, value: str):
        # TODO: refactor !!!
        try:
            self.formatted_time = datetime.strptime(
                str(value), "%Y-%m-%d %H:%M"
            ).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            self.formatted_time = value

    @property
    def application_worker_ids(self):
        return [application.worker_id for application in self.applications]

    def __repr__(self):
        return f"<{self.id}: {self.name}>"

    @orm.validates("payment_status")
    def validate_commission_status(self, key, value):
        if (
            self.payment_status == s.enums.PaymentStatus.PAID
            and value != s.enums.PaymentStatus.PAID
        ):
            raise ValueDownGradeForbidden(
                "Payment status can only be PAID if payment status is PAID"
            )
        return value

    @orm.validates("commission_status")
    def validate_payment_status(self, key, value):
        if (
            self.commission_status == s.enums.CommissionStatus.PAID
            and value != s.enums.CommissionStatus.PAID
        ):
            raise ValueDownGradeForbidden(
                "Commission status can only be PAID if commission status is PAID"
            )
        return value
