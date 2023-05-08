from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils import generate_uuid
from app import schema as s


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    uuid = Column(String(36), default=generate_uuid)

    owner_id = Column(ForeignKey("users.id"), nullable=False)
    worker_id = Column(ForeignKey("users.id"), nullable=True)
    profession_id = Column(ForeignKey("professions.id"), nullable=True)

    name = Column(String(64), default="")
    description = Column(String(512), default="")
    is_deleted = Column(Boolean, default=False)

    status = Column(Enum(s.Job.Status), default=s.Job.Status.PENDING)
    payment_status = Column(
        Enum(s.Job.PaymentStatus), default=s.Job.PaymentStatus.UNPAID
    )
    commission_status = Column(
        Enum(s.Job.CommissionStatus), default=s.Job.CommissionStatus.UNPAID
    )

    created_at = Column(DateTime, default=datetime.now)

    worker = relationship("User", foreign_keys=[worker_id], viewonly=True)
    owner = relationship("User", foreign_keys=[owner_id], viewonly=True)
    profession = relationship("Profession", viewonly=True)

    def __repr__(self):
        return f"<{self.id}: {self.name}>"
