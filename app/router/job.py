from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s

from app.database import get_db

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])


@job_router.get("", status_code=201, response_model=s.ListJob)
def get_jobs(db: Session = Depends(get_db)):
    jobs: list[m.Job] = db.scalars(select(m.Job).order_by(m.Job.id)).all()
    return s.ListJob(jobs=jobs)
