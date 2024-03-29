import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid

from app import model as m
from .platform_payment import PlatformPayment


class PlatformCommission(db.Model):
    __tablename__ = "platform_commissions"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        default=generate_uuid,
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    platform_payment_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("platform_payments.id"),
        nullable=False,
    )

    # relationships
    user: orm.Mapped[m.User] = orm.relationship(
        "User",
        foreign_keys=[user_id],
        viewonly=True,
        backref="platform_commissions",
        uselist=False,
    )
    platform_payment: orm.Mapped[PlatformPayment] = orm.relationship(
        "PlatformPayment",
        foreign_keys=[platform_payment_id],
        backref="platform_commissions",
        viewonly=True,
        uselist=False,
    )
