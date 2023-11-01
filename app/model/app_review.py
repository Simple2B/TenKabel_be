from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import orm

from app.database import db
from app.utility import generate_uuid


class AppReview(db.Model):
    __tablename__ = "app_reviews"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(
        sa.String(36),
        unique=True,
        index=True,
        default=generate_uuid,
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=True
    )

    stars_count: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)
    review: orm.Mapped[str] = orm.mapped_column(sa.String(1000), nullable=False)

    created_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
    )
    user = orm.relationship("User")

    def __str__(self) -> str:
        return f"User[{self.user_id}] - [{self.stars_count}] stars"
