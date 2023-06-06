import re

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependency import get_current_user, get_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db

job_router = APIRouter(prefix="/job", tags=["Jobs"])


@job_router.get(
    "/status_list", status_code=status.HTTP_200_OK, response_model=list[str]
)
def get_status_list():
    return [e.value for e in s.Job.Status]


@job_router.get("/jobs", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_jobs(
    profession_id: int = None,
    city: str = None,
    min_price: int = None,
    max_price: int = None,
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_user),
) -> s.ListJob:
    query = select(m.Job).where(m.Job.status == s.Job.Status.PENDING)
    if (
        user is None
        or user.google_openid_key
        or any([profession_id, city, min_price, max_price])
    ):
        if profession_id:
            query = query.where(m.Job.profession_id == profession_id)
        if city:
            city = re.sub(r"[^a-zA-Z0-9]", "", city)
            query = query.where(m.Job.city.ilike(f"%{city}%"))
        if min_price:
            query = query.where(m.Job.payment >= min_price)
        if max_price:
            query = query.where(m.Job.payment <= max_price)
        log(log.INFO, "Job filtered")
    else:
        profession_ids: list[int] = [profession.id for profession in user.professions]
        cities_names: list[str] = [location.name_en for location in user.locations]
        if profession_ids:
            filter_conditions = []
            for prof_id in profession_ids:
                filter_conditions.append(m.Job.profession_id == prof_id)
            query = query.filter(or_(*filter_conditions))

            log(
                log.INFO,
                "Job filtered by profession ids [%s] user interests",
                profession_ids,
            )
        if cities_names:
            filter_conditions = []
            for location in cities_names:
                filter_conditions.append(m.Job.city.ilike(location))
            query = query.filter(or_(*filter_conditions))
            log(
                log.INFO,
                "Job filtered by cities names [%s] user interests",
                location,
            )
        if not cities_names and not profession_ids:
            log(log.INFO, "Job returned with no filters")

    jobs: list[m.Job] = db.scalars(query.order_by(m.Job.id)).all()
    log(log.INFO, "Job [%s] at all got", len(jobs))
    return s.ListJob(jobs=jobs)


@job_router.get("/search", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def search_job(
    q: str | None = "",
    db: Session = Depends(get_db),
) -> s.ListJob:
    query = select(m.Job).where(m.Job.status == s.Job.Status.PENDING)

    if q:
        query = query.where(
            or_(
                m.Job.name.icontains(f"%{q}%"),
                m.Job.description.icontains(f"%{q}%"),
                m.Job.city.icontains(f"%{q}%"),
            )
        )

    log(log.INFO, "Job filtered by [%s] containing", q)
    return s.ListJob(jobs=db.scalars(query.order_by(m.Job.created_at.desc())).all())


@job_router.get("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def get_job(
    job_uuid: str,
    db: Session = Depends(get_db),
) -> s.Job:
    job: m.Job | None = db.scalars(select(m.Job).where(m.Job.uuid == job_uuid)).first()
    if not job:
        log(log.INFO, "Job wasn`t found [%s]", job_uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    log(log.INFO, "Job [%s] info", job_uuid)
    return job


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
        customer_first_name=data.customer_first_name,
        customer_last_name=data.customer_last_name,
        customer_phone=data.customer_phone,
        customer_street_address=data.customer_street_address,
    )
    db.add(new_job)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new job"
        )

    log(log.INFO, "Job [%s] created successfully", new_job.id)
    return status.HTTP_201_CREATED


@job_router.put("/{job_uuid}", status_code=status.HTTP_200_OK)
def update_job(
    job_data: s.JobUpdate,
    job_uuid: str,
    db: Session = Depends(get_db),
):
    job: m.Job | None = db.scalars(select(m.Job).where(m.Job.uuid == job_uuid)).first()
    if not job:
        log(log.INFO, "Job [%s] wasn`t found", job_uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    job.profession_id = job_data.profession_id
    job.city = job_data.city
    job.payment = job_data.payment
    job.commission = job_data.commission
    job.name = job_data.name
    job.description = job_data.description
    job.time = job_data.time
    job.customer_first_name = job_data.customer_first_name
    job.customer_last_name = job_data.customer_last_name
    job.customer_phone = job_data.customer_phone
    job.customer_street_address = job_data.customer_street_address

    job.status = s.Job.Status(job_data.status)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating job"
        )

    log(log.INFO, "Job [%s] updated successfully", job.name)
    return status.HTTP_200_OK
