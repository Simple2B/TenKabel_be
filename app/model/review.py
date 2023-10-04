import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s
from app import model as m


class Review(db.Model):
    __tablename__ = "reviews"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        default=generate_uuid,
    )
    evaluated_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    evaluates_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )

    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("jobs.id"), nullable=False
    )
    tag_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tags.id"), nullable=False
    )

    rate: orm.Mapped[s.BaseRate.RateStatus] = orm.mapped_column(
        sa.Enum(s.BaseRate.RateStatus), default=s.BaseRate.RateStatus.NEUTRAL
    )

    job: orm.Mapped[m.Job] = orm.relationship(
        "Job", foreign_keys=[job_id], viewonly=True, backref="reviews"
    )
    tag: orm.Mapped[m.Tag] = orm.relationship()

    def __repr__(self):
        return f"<{self.id}: {self.rate}>"
