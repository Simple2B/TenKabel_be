import sqlalchemy as sa
from sqlalchemy import orm, select

import app.schema as s

from app.database import db
from app.utility import generate_uuid


class Notification(db.Model):
    __tablename__ = "notifications"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer, primary_key=True)
    uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)
    type: orm.Mapped[s.NotificationType] = orm.mapped_column(
        sa.Enum(s.NotificationType), nullable=False
    )
    entity_id: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=False)
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), nullable=True
    )

    user = orm.relationship("User", backref="notifications")

    def create_schema(
        self, session: orm.Session
    ) -> s.NotificationJob | s.NotificationApplication:
        from app.model import Job, Application

        if self.type < s.NotificationType.MAX_JOB_TYPE:
            return s.NotificationJob(
                id=self.id,
                type=self.type,
                payload=session.scalar(select(Job).filter(Job.id == self.entity_id)),
            )
        return s.NotificationApplication(
            id=self.id,
            type=self.type,
            payload=session.scalar(
                select(Application).filter(Application.id == self.entity_id),
            ),
        )
