import sqlalchemy as sa

from app.database import db


users_professions = sa.Table(
    "users_professions",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("profession_id", sa.ForeignKey("professions.id"), primary_key=True),
)
