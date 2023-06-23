import sqlalchemy as sa

from app.database import db


users_notifications_locations = sa.Table(
    "users_notifications_locations",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("location_id", sa.ForeignKey("locations.id"), primary_key=True),
)


class UserNotificationLocation(db.Model):
    __tablename__ = "users_notifications_locations"
