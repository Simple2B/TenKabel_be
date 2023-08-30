from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s
from app import model as m


class Application(db.Model):
    __tablename__ = "applications"

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
    owner_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    worker_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=True
    )

    status: orm.Mapped[s.BaseApplication.ApplicationStatus] = orm.mapped_column(
        sa.Enum(s.BaseApplication.ApplicationStatus),
        default=s.BaseApplication.ApplicationStatus.PENDING,
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )

    status_changed_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )

    worker: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[worker_id], viewonly=True
    )
    owner: orm.Mapped[m.User] = orm.relationship(
        "User", foreign_keys=[owner_id], viewonly=True
    )

    @property
    def job_uuid(self) -> str:
        return self.job.uuid

    @property
    def job_name(self) -> str:
        return self.job.name

    @property
    def job_status(self):
        return self.job.status

    @orm.validates("status")
    def update_status_changed_at(self, key, value):
        if self.status != value:
            self.status_changed_at = datetime.utcnow()
        return value
