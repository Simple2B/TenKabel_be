from pydantic import BaseModel


import app.model as m
from .user import User


class BaseJob(BaseModel):
    owner_id: int
    worker_id: int
    profession_id: int

    name: str
    description: str


class Job(BaseJob):
    status: m.Job.JobStatus
    payment_status: m.Job.PaymentStatus
    commission_status: m.Job.CommissionStatus
    is_deleted: bool
    owner: User
    worker: User
