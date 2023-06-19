import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from .user import User


class Device(db.Model):
    __tablename__ = "devices"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36), nullable=False, unique=True
    )  # no default for this field. It should be provided by frontend
    push_token: orm.Mapped[str] = orm.mapped_column(sa.String(256), nullable=False)
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=False
    )
    user: orm.Mapped[User] = orm.relationship(
        "User", backref="devices", foreign_keys=[user_id], viewonly=True
    )
