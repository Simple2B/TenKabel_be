import sqlalchemy as sa

from app.database import db


users_locations = sa.Table(
    "users_locations",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("location_id", sa.ForeignKey("locations.id"), primary_key=True),
)


class UserLocation(db.Model):
    __tablename__ = "users_locations"
