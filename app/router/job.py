from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s

from app.database import get_db

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])


@job_router.get("", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_jobs(
    profession_id: int = None,
    city: str = None,
    min_price: int = None,
    max_price: int = None,
    db: Session = Depends(get_db),
):
    query = select(m.Job)
    if profession_id:
        query = query.where(m.Job.profession_id == profession_id)
    if city:
        query = query.where(m.Job.city.ilike(f"%{city}%"))
    if min_price:
        query = query.where(m.Job.payment >= min_price)
    if max_price:
        query = query.where(m.Job.payment <= max_price)
    return s.ListJob(jobs=db.scalars(query.order_by(m.Job.id)).all())
