from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid

from app import schema as s
from app.config import Settings, get_settings
from .user import User

settings: Settings = get_settings()


class PlatformPayment(db.Model):
    __tablename__ = "platform_payments"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

    transaction_number: orm.Mapped[str] = orm.mapped_column(
        sa.String(64), nullable=True
    )
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )  # payer_id
    status: orm.Mapped[s.enums.PlatformPaymentStatus] = orm.mapped_column(
        sa.Enum(s.enums.PlatformPaymentStatus),
        default=s.enums.PlatformPaymentStatus.UNPAID,
    )
    reject_reason: orm.Mapped[str] = orm.mapped_column(
        sa.String(512), default=""
    )  # reason of rejection
    created_at = orm.mapped_column(sa.DateTime(), default=datetime.now)
    paid_at: orm.Mapped[sa.DateTime] = orm.mapped_column(sa.DateTime(), nullable=True)
    rejected_at: orm.Mapped[sa.DateTime] = orm.mapped_column(
        sa.DateTime(), nullable=True
    )

    user: orm.Mapped[User] = orm.relationship(
        "User", foreign_keys=[user_id], backref="platform_payments"
    )

    def __repr__(self):
        return f"<PlatformPayment {self.id} - {self.status}>"
