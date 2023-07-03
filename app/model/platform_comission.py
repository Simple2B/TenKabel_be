import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid

from app import model as m
from .platform_payment import PlatformPayment


class PlatformComission(db.Model):
    __tablename__ = "platform_comissions"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    platform_payment_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("platform_payments.id"),
        nullable=True,  # TODO conside change to False?
    )
    # relationship
    user: orm.Mapped[m.User] = orm.relationship(
        "User",
        foreign_keys=[user_id],
        viewonly=True,
        uselist=False,
    )
    platform_payment: orm.Mapped[PlatformPayment] = orm.relationship(
        "PlatformPayment",
        foreign_keys=[platform_payment_id],
        backref="platform_comissions",
        viewonly=True,
        uselist=False,
    )
