import sqlalchemy as sa

from app.database import db


users_rates = sa.Table(
    "users_rates",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("rate_id", sa.ForeignKey("rate.id"), primary_key=True),
)
