import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid


class Profession(db.Model):
    __tablename__ = "professions"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        default=generate_uuid,
    )
    name_en: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")
    name_hebrew: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")

    is_deleted: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    def __repr__(self):
        return f"<{self.id}: {self.name_en}>"
