from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s
from app import model as m
from app.model.applications import Application


class PlatformPayment(db.Model):
    __tablename__ = "platform_payments"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )

    status: orm.Mapped[s.enums.PlatformPaymentStatus] = orm.mapped_column(
        sa.Enum(s.enums.PlatformPaymentStatus),
        default=s.enums.PlatformPaymentStatus.IDLE,
    )

    # relationship
    user: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[id], viewonly=True, backref="users"
    )

    job: orm.Mapped[m.User] = orm.relationship(
        "Job", foreign_keys=[id], viewonly=True, backref="jobs"
    )
