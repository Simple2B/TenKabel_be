from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid


class DeviceToken(db.Model):
    __tablename__ = "device_tokens"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)

    token: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    user_id: orm.Mapped[id] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )

    def __repr__(self):
        return f"<{self.id}: {self.user_id}>"
