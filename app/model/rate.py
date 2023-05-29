import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s


class Rate(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    rate: orm.Mapped[s.Rate.RateStatus] = orm.mapped_column(
        sa.Enum(s.Rate.RateStatus), default=s.Rate.RateStatus.NEUTRAL
    )

    def __repr__(self):
        return f"<{self.id}: {self.rate}>"
