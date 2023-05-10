from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utils import generate_uuid
from app import schema as s

from .user import User
from .profession import Profession


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
    status: orm.Mapped[s.Job.Status] = orm.mapped_column(
        sa.Enum(s.Job.Status), default=s.Job.Status.PENDING
    )
    payment_status: orm.Mapped[s.Job.PaymentStatus] = orm.mapped_column(
        sa.Enum(s.Job.PaymentStatus), default=s.Job.PaymentStatus.UNPAID
    )
    commission_status: orm.Mapped[s.Job.CommissionStatus] = orm.mapped_column(
        sa.Enum(s.Job.CommissionStatus), default=s.Job.CommissionStatus.UNPAID
    )
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )
    worker: orm.Mapped[User] = orm.relationship(
        "User", foreign_keys=[worker_id], viewonly=True
    )
    owner: orm.Mapped[User] = orm.relationship(
        "User", foreign_keys=[owner_id], viewonly=True
    )
    profession: orm.Mapped[Profession] = orm.relationship("Profession", viewonly=True)

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
