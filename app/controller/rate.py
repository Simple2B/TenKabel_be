from app import model as m
from app import schema as s
from app.database import db
from app.logger import log
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status, HTTPException


def create_rate_controller(rate_data: s.BaseRate, db: Session):
    job: m.Job | None = db.scalar(select(m.Job).where(m.Job.id == rate_data.job_id))
    if not job:
        log(log.INFO, "Job [%s] wasn`t found ", rate_data.job_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job not found",
        )
    owner: m.User | None = db.scalar(
        select(m.User).where(m.User.id == rate_data.owner_id)
    )
    if not owner:
        log(log.INFO, "User [%s] wasn`t found ", rate_data.owner_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User not found"
        )
    worker: m.User | None = db.scalar(
        select(m.User).where(m.User.id == rate_data.worker_id)
    )
    if not worker:
        log(log.INFO, "User [%s] wasn`t found ", rate_data.worker_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User not found"
        )

    if worker not in (job.owner, job.worker) or owner not in (job.owner, job.worker):
        log(
            log.INFO,
            "User [%s] or [%s] is not in job [%s]",
            rate_data.owner_id,
            rate_data.worker_id,
            rate_data.job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User is not in job"
        )

    new_rate: m.Rate = m.Rate(
        job_id=rate_data.job_id,
        owner_id=rate_data.owner_id,
        worker_id=rate_data.worker_id,
        rate=s.BaseRate.RateStatus(rate_data.rate),
    )

    db.add(new_rate)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new rate - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new rate"
        )

    log(log.INFO, "Rate [%s] created successfully", new_rate.id)
    return new_rate
