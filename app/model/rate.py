import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s
from app import model as m


class Rate(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    owner_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    worker_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    rate: orm.Mapped[s.BaseRate.RateStatus] = orm.mapped_column(
        sa.Enum(s.BaseRate.RateStatus), default=s.BaseRate.RateStatus.NEUTRAL
    )

    worker: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[worker_id], viewonly=True, backref="gived_rates"
    )
    owner: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[owner_id], viewonly=True, backref="owned_rates"
    )
    job: orm.Mapped[m.Job] = orm.relationship(
        "Job", foreign_keys=[job_id], viewonly=True, backref="rates"
    )

    def __repr__(self):
        return f"<{self.id}: {self.rate}>"
