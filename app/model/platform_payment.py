from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s


class PlatformPayment(db.Model):
    __tablename__ = "platform_payments"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

    type: orm.Mapped[s.enums.PlatformPaymentPeriod] = orm.mapped_column(
        sa.Enum(s.enums.PlatformPaymentPeriod),
        default=s.enums.PlatformPaymentPeriod.WEEKLY,
    )
    status: orm.Mapped[s.enums.PlatformPaymentStatus] = orm.mapped_column(
        sa.Enum(s.enums.PlatformPaymentStatus),
        default=s.enums.PlatformPaymentStatus.UNPAID,
    )
    reject: orm.Mapped[str] = orm.mapped_column(
        sa.String(512), default=""
    )  # reason of rejection
    created_at = orm.mapped_column(sa.DateTime(), default=datetime.now)
    paid_at: orm.Mapped[sa.DateTime] = orm.mapped_column(sa.DateTime(), nullable=True)
    rejected_at: orm.Mapped[sa.DateTime] = orm.mapped_column(
        sa.DateTime(), nullable=True
    )
