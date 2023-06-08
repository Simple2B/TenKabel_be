import base64
import re
from datetime import datetime
from typing import Self

import sqlalchemy as sa
from sqlalchemy import orm

from app.hash_utils import make_hash, hash_verify
from app.utility import generate_uuid, get_default_avatar


class BaseUser:
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    email: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=True, unique=True
    )
    username: orm.Mapped[str] = orm.mapped_column(sa.String(128), default="")
    google_openid_key: orm.Mapped[str] = orm.mapped_column(sa.String(64), nullable=True)
    avatar_decoded: orm.Mapped[str] = orm.mapped_column(
        sa.Text, default=get_default_avatar()
    )

    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(128), nullable=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )
    is_verified: orm.Mapped[bool] = orm.mapped_column(sa.Boolean, default=True)

    @property
    def picture(self):
        return base64.b64encode(self.avatar_decoded)

    @picture.setter
    def picture(self, value: str):
        # check for http url
        if isinstance(value, str) and re.search(r"^(http|https)://", value):
            self.avatar_decoded = value
        else:
            self.avatar_decoded = base64.b64decode(value)

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
        if user is not None and hash_verify(password, user.password):
            return user

    def __repr__(self):
        return f"<{self.id}: {self.username}>"
