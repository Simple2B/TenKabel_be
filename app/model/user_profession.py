from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime


from app.database import Base
from app.utils import generate_uuid


class UserProfession(Base):
    __tablename__ = "users_professions"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), default=generate_uuid)

    user_id = Column(ForeignKey("users.id"), nullable=False)
    profession_id = Column(ForeignKey("professions.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
