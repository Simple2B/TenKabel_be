from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s


class Commission(db.Model):
    __tablename__ = "commissions"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    commission_status: orm.Mapped[s.enums.CommissionStatus] = orm.mapped_column(
        sa.Enum(s.enums.CommissionStatus), default=s.enums.CommissionStatus.UNPAID
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )
