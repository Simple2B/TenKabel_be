from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base
from app.utils import generate_uuid


class UserLocation(Base):
    __tablename__ = "users_locations"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), default=generate_uuid)

    user_id = Column(ForeignKey("users.id"), nullable=False)
    location_id = Column(ForeignKey("locations.id"), nullable=False)

    name = Column(String(64), default="")

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
