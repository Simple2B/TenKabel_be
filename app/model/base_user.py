from datetime import datetime
from typing import Self

import sqlalchemy as sa
from sqlalchemy import orm

from app.hash_utils import make_hash, hash_verify
from app.utility import generate_uuid, get_default_avatar
from app.logger import log


class BaseUser:
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        default=generate_uuid,
    )
    email: orm.Mapped[str] = orm.mapped_column(
        sa.String(128),
        nullable=True,
        index=True,
        unique=True,
    )
    username: orm.Mapped[str] = orm.mapped_column(sa.String(128), default="")
    google_openid_key: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=True)
    apple_uid: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=True)
    picture: orm.Mapped[str] = orm.mapped_column(sa.Text, default=get_default_avatar())

    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(128), nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )
    country_code: orm.Mapped[str] = orm.mapped_column(sa.String(32))
    is_verified: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=True)
    is_deleted: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=False)

    @property
    def is_auth_by_google(self) -> bool:
        return bool(self.google_openid_key)

    @property
    def is_auth_by_apple(self) -> bool:
        return bool(self.apple_uid)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, value: str):
        self.password_hash = make_hash(value)

    @classmethod
    def authenticate(cls, db: orm.Session, user_id: str, password: str) -> Self:
        user = (
            db.query(cls)
            .filter(
                sa.or_(
                    sa.func.lower(cls.username) == sa.func.lower(user_id),
                    sa.func.lower(cls.email) == sa.func.lower(user_id),
                )
            )
            .first()
        )

        if user.is_deleted:
            log(log.INFO, "User is deleted")
            return None

        if user is not None and (
            hash_verify(password, user.password) or password == user.password
        ):
            return user

    def __repr__(self):
        return f"<{self.id}: {self.username}>"
