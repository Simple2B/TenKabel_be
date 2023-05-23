from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependency import get_current_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db

job_router = APIRouter(prefix="/job", tags=["Jobs"])


@job_router.get("/jobs", status_code=status.HTTP_200_OK, response_model=s.ListJob)
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


@job_router.get("/{job_uuid}/", status_code=status.HTTP_200_OK, response_model=s.Job)
def get_job(
    job_uuid: str,
    db: Session = Depends(get_db),
):
    job: m.Job | None = db.scalars(select(m.Job)).first()
    if not job:
        log(log.INFO, "Job wasn`t found %s", job_uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@job_router.get("/search", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def search_job(
    title: str | None = None,
    city: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(m.Job)

    if title:
        query = query.where(
            or_(
                m.Job.name.icontains(f"%{title}%"),
                m.Job.description.icontains(f"%{title}%"),
            )
        )
    if city:
        query = query.where(m.Job.city.icontains(f"%{city}%"))

    return s.ListJob(jobs=db.scalars(query.order_by(m.Job.created_at.desc())).all())


@job_router.post("", status_code=status.HTTP_201_CREATED)
def create_job(
    data: s.JobIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    new_job = m.Job(
        owner_id=current_user.id,
        profession_id=data.profession_id,
        name=data.name,
        description=data.description,
        payment=data.payment,
        commission=data.commission,
        city=data.city,
        time=data.time,
    )
    db.add(new_job)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new job"
        )

    return status.HTTP_201_CREATED
