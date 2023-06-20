import sqlalchemy as sa

from datetime import datetime
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
    created_at: orm.Mapped[sa.DateTime] = orm.mapped_column(
        sa.DateTime, default=datetime.utcnow
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

        if s.NotificationType.get_index(self.type) < s.NotificationType.get_index(
            s.NotificationType.MAX_JOB_TYPE
        ):
            return s.NotificationJob(
                id=self.id,
                uuid=self.uuid,
                user_id=self.user_id,
                type=self.type,
                payload=session.scalar(select(Job).filter(Job.id == self.entity_id)),
                created_at=self.created_at,
            )
        return s.NotificationApplication(
            id=self.id,
            uuid=self.uuid,
            user_id=self.user_id,
            type=self.type,
            payload=session.scalar(
                select(Application).filter(Application.id == self.entity_id),
            ),
            created_at=self.created_at,
        )
