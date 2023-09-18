from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.exceptions import ValueDownGradeForbidden
from app.utility import generate_uuid
from app import schema as s
from app import model as m
from app.model.applications import Application
from .platform_commission import PlatformCommission
from .attachment import Attachment
from .job_location import jobs_locations
from .location import Location


class Job(db.Model):
    __tablename__ = "jobs"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )

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

    regions: orm.Mapped[Location] = orm.relationship(
        "Location", secondary=jobs_locations, viewonly=True
    )
    city: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)
    formatted_time: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=False)

    is_asap: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)
    frame_time: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=True)

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

    # timestamps of status changes
    # job progress screen
    pending_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True, default=datetime.utcnow
    )  # could be application changed_at
    approved_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, nullable=True)
    in_progress_at: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, nullable=True)
    job_is_finished_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )
    # payment screen
    # TODO: find why does design have 2 different payment screens
    payment_unpaid_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )  # could be self.created_at
    payment_paid_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )

    # commission screen
    commission_sent_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )
    commission_confirmation_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )
    commission_denied_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
    )
    commission_approved_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=True
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

    # worker_attachments: orm.Mapped[m.Attachment] = orm.relationship(
    #     "Attachment",
    #     foreign_keys=[worker_attachments_id],
    #     viewonly=True,
    # )
    # owner_attachments: orm.Mapped[m.Attachment] = orm.relationship(
    #     "Attachment",
    #     foreign_keys=[owner_attachments_id],
    #     viewonly=True,
    # )
    platform_commissions: orm.Mapped[PlatformCommission] = orm.relationship(
        "PlatformCommission", backref="job"
    )

    profession: orm.Mapped[m.Profession] = orm.relationship("Profession", viewonly=True)
    attachments: orm.Mapped[list[Attachment]] = orm.relationship(
        "Attachment", backref="job"
    )

    def __repr__(self):
        return f"<{self.id}: {self.name}>"

    def set_enum(
        self, enum: s.enums.JobStatus | s.enums.PaymentStatus | s.enums.CommissionStatus
    ):
        if isinstance(enum, s.enums.JobStatus):
            if enum == s.enums.JobStatus.APPROVED:
                self.approved_at = datetime.utcnow()
            elif enum == s.enums.JobStatus.IN_PROGRESS:
                self.in_progress_at = datetime.utcnow()
            elif enum == s.enums.JobStatus.JOB_IS_FINISHED:
                self.job_is_finished_at = datetime.utcnow()
            self.status = enum
        elif isinstance(enum, s.enums.PaymentStatus):
            if enum == s.enums.PaymentStatus.PAID:
                self.payment_paid_at = datetime.utcnow()
            elif enum == s.enums.PaymentStatus.UNPAID:
                self.payment_unpaid_at = datetime.utcnow()
            # recheck design
            # elif enum == s.enums.PaymentStatus.DENY:
            #     self.payment_denied_at = datetime.utcnow()
            self.payment_status = enum
        elif isinstance(enum, s.enums.CommissionStatus):
            if enum == s.enums.CommissionStatus.PAID:
                self.commission_sent_at = datetime.utcnow()
            elif enum == s.enums.CommissionStatus.UNPAID:
                self.commission_confirmation_at = datetime.utcnow()
            elif enum == s.enums.CommissionStatus.DENY:
                self.commission_denied_at = datetime.utcnow()
            elif enum == s.enums.CommissionStatus.CONFIRM:
                self.commission_approved_at = datetime.utcnow()
            self.commission_status = enum
        else:
            raise TypeError(f"Enum {enum} is not supported")

    @property
    def owner_rate_uuid(self) -> str | None:
        rates = [rate for rate in self.rates if rate.worker_id == self.owner_id]
        return rates[0].uuid if rates else None

    @property
    def worker_rate_uuid(self) -> str | None:
        rates = [rate for rate in self.rates if rate.worker_id == self.worker_id]
        return rates[0].uuid if rates else None

    @property
    def time(self) -> str:
        return self.formatted_time

    @time.setter
    def time(self, value: str):
        try:
            self.formatted_time = datetime.strptime(
                str(value), "%Y-%m-%d %H:%M"
            ).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            self.formatted_time = value

    @property
    def application_worker_ids(self):
        return [application.worker_id for application in self.applications]

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

    @property
    def owner_attachments(self) -> list[Attachment]:
        result = []
        for attachment in self.attachments:
            if attachment.created_by_id == self.owner_id:
                result.append(attachment)
        return result

    @property
    def worker_attachments(self) -> list[Attachment]:
        result = []
        for attachment in self.attachments:
            if attachment.created_by_id == self.worker_id:
                result.append(attachment)
        return result
