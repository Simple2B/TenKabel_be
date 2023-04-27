from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime

from app.database import Base


class JobLocation(Base):
    __tablename__ = "jobs_locations"

    id = Column(Integer, primary_key=True)

    job_id = Column(ForeignKey("jobs.id"), nullable=False)
    location_id = Column(ForeignKey("locations.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
