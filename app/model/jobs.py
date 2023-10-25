from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm


from app.database import db
from app.exceptions import ValueDownGradeForbidden
from app.utility import generate_uuid
from app import schema as s
from app.model.applications import Application
from .job_location import jobs_locations
from .payment import Payment
from .commission import Commission
from .job_status import JobStatus
from .location import Location
from .platform_commission import PlatformCommission

if TYPE_CHECKING:
    from .attachment import Attachment
    from .profession import Profession
    from .user import User


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

    commission_symbol: orm.Mapped[s.enums.CommissionSymbol] = orm.mapped_column(
        sa.Enum(s.enums.CommissionSymbol),
        nullable=True,
        default=None,
        server_default=None,
    )

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

    payments: orm.Mapped[list["Payment"]] = orm.relationship()
    commissions: orm.Mapped[list["Commission"]] = orm.relationship()
    statuses: orm.Mapped[list["JobStatus"]] = orm.relationship()

    # relationships
    applications: orm.Mapped[list["Application"]] = orm.relationship(
        "Application", viewonly=True, backref="job"
    )
    worker: orm.Mapped["User"] = orm.relationship(
        "User", foreign_keys=[worker_id], viewonly=True, backref="jobs_to_do"
    )
    owner: orm.Mapped["User"] = orm.relationship(
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

    profession: orm.Mapped["Profession"] = orm.relationship("Profession", viewonly=True)
    attachments: orm.Mapped[list["Attachment"]] = orm.relationship(
        "Attachment", backref="job"
    )

    def __repr__(self):
        return f"<{self.id}: {self.name}>"

    def set_enum(
        self,
        enum: s.enums.JobStatus | s.enums.PaymentStatus | s.enums.CommissionStatus,
        db: orm.Session,
    ):
        if isinstance(enum, s.enums.JobStatus):
            job_status = JobStatus(job_id=self.id, status=enum)
            self.status = enum
            db.add(job_status)

        elif isinstance(enum, s.enums.PaymentStatus):
            payment = Payment(job_id=self.id, payment_status=enum)
            self.payment_status = enum
            db.add(payment)

        elif isinstance(enum, s.enums.CommissionStatus):
            commission = Commission(job_id=self.id, commission_status=enum)
            self.commission_status = enum
            db.add(commission)

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
    def owner_review_uuid(self) -> str | None:
        reviews = [
            review for review in self.reviews if review.evaluates_id == self.worker_id
        ]
        return reviews[0].uuid if reviews else None

    @property
    def worker_review_uuid(self) -> str | None:
        reviews = [
            review for review in self.reviews if review.evaluates_id == self.owner_id
        ]
        return reviews[0].uuid if reviews else None

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
    def owner_attachments(self) -> list["Attachment"]:
        result = []
        for attachment in self.attachments:
            if attachment.created_by_id == self.owner_id:
                result.append(attachment)
        return result

    @property
    def worker_attachments(self) -> list["Attachment"]:
        result = []
        for attachment in self.attachments:
            if attachment.created_by_id == self.worker_id:
                result.append(attachment)
        return result
