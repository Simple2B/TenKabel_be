from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid
from app import schema as s


class File(db.Model):
    __tablename__ = "files"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id"),
    )

    original_filename: orm.Mapped[str] = orm.mapped_column(
        sa.String(256), nullable=False
    )

    url: orm.Mapped[str] = orm.mapped_column(
        sa.String(256),
        unique=True,
        nullable=False,
    )

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, nullable=False, default=datetime.utcnow
    )

    is_deleted: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
    )

    # user: orm.Mapped["User"] = orm.relationship(  # noqa: F821
    #     "User",
    #     back_populates="files",
    # )

    @property
    def storage_path(self) -> str:
        return f"attachments/{self.user.uuid}/{self.original_filename}"

    @property
    def filename(self) -> str:
        return f"{self.uuid}_{self.original_filename}"

    @property
    def type(self) -> s.enums.AttachmentType:
        if self.extension in [e.value for e in s.enums.ImageExtension]:
            return s.enums.AttachmentType.IMAGE
        return s.enums.AttachmentType.DOCUMENT

    @property
    def extension(self) -> str:
        return self.filename.split(".")[-1]

    def __str__(self):
        return self.filename

    def __repr__(self):
        return f"<File {self.id} - {self.filename}>"
