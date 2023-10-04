from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s


class Tag(db.Model):
    __tablename__ = "tags"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )

    rate: orm.Mapped[s.BaseRate.RateStatus] = orm.mapped_column(
        sa.Enum(s.BaseRate.RateStatus), default=s.BaseRate.RateStatus.NEUTRAL
    )
    profession_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("professions.id"), nullable=False
    )
    tag: orm.Mapped[str] = orm.mapped_column(sa.String(100), nullable=False)

    @orm.validates("status")
    def update_status_changed_at(self, key, value):
        if self.status != value:
            self.status_changed_at = datetime.utcnow()
        return value
