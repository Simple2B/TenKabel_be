from datetime import datetime

# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

import sqlalchemy as sa

from app.database import db


users_professions = sa.Table(
    "users_professions",
    db.Model.metadata,
    sa.Column("user_id", sa.ForeignKey("users.id"), primary_key=True),
    sa.Column("profession_id", sa.ForeignKey("professions.id"), primary_key=True),
)


# class UserProfession(db.Model):
#     __tablename__ = "users_professions"

#     id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

#     # id = Column(Integer, primary_key=True)

#     uuid: orm.Mapped[str] = orm.mapped_column(sa.String(36), default=generate_uuid)

#     # uuid = Column(String(36), default=generate_uuid)

#     user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id"), index=True)

#     # user_id = Column(ForeignKey("users.id"), nullable=False)

#     profession_id: orm.Mapped[int] = orm.mapped_column(
#         sa.ForeignKey("professions.id"), index=True
#     )

#     # profession_id = Column(ForeignKey("professions.id"), nullable=False)

#     created_at: orm.Mapped[datetime] = orm.mapped_column(
#         sa.DateTime, default=datetime.utcnow
#     )

#     # created_at = Column(DateTime, default=datetime.now)

#     # def __repr__(self):
#     #     return f"<{self.id}: {self.name}>"
