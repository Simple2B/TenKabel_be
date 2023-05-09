import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utils import generate_uuid


class Profession(db.Model):
    __tablename__ = "professions"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(64), default="")

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
