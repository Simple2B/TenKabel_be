from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid

from app import schema as s


class Attachment(db.Model):
    __tablename__ = "attachments"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )
    job_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        sa.ForeignKey("jobs.id"),
        nullable=True,
    )
    created_by_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id"),
        nullable=True,
    )

    filename: orm.Mapped[str] = orm.mapped_column(sa.String(255), nullable=False)
    original_filename: orm.Mapped[str] = orm.mapped_column(
        sa.String(255), nullable=False
    )
    storage_path: orm.Mapped[str] = orm.mapped_column(sa.String(512), nullable=True)
    extension: orm.Mapped[str] = orm.mapped_column(sa.String(32), nullable=False)
    url: orm.Mapped[str] = orm.mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
    )
    type: orm.Mapped[s.enums.AttachmentType] = orm.mapped_column(
        sa.Enum(s.enums.AttachmentType),
        nullable=False,
        default=s.enums.AttachmentType.IMAGE,
    )

    uploaded_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    def __str__(self):
        return self.filename
