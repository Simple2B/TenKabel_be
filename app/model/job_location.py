from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from app.database import db


class JobLocation(db.Model):
    __tablename__ = "jobs_locations"
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    location_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("locations.id"), nullable=False
    )
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default_factory=datetime.utcnow
    )

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
