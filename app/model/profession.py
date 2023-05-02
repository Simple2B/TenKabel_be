from sqlalchemy import Column, Integer, String

from app.database import Base
from app.utils import generate_uuid


class Profession(Base):
    __tablename__ = "professions"
    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), default=generate_uuid)

    name = Column(String(64), default="")

    def __repr__(self):
        return f"<{self.id}: {self.name}>"