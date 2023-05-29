from fastapi import HTTPException, Depends, APIRouter, status

from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user
from app.database import get_db

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    current_user: m.User = Depends(get_current_user),
):
    return current_user


@user_router.get("/jobs", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_user_jobs(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    """Get list of jobs where current user is a worker"""
    jobs: list[m.Job] = db.scalars(
        select(m.Job)
        .order_by(m.Job.created_at)
        .where(m.Job.worker_id == current_user.id)
    ).all()
    return s.ListJob(jobs=jobs)


@user_router.get("/rates", status_code=status.HTTP_200_OK, response_model=s.RateList)
def get_user_rates(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    rates: s.RateList = db.scalars(
        select(m.Rate).where(m.Rate.user_id == current_user.id)
    ).all()
    return s.RateList(rates=rates)


@user_router.get("/postings", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_user_postings(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    """Get list of jobs where current user is a worker"""
    jobs: list[m.Job] = db.scalars(
        select(m.Job)
        .order_by(m.Job.created_at)
        .where(m.Job.owner_id == current_user.id)
    ).all()
    return s.ListJob(jobs=jobs)


@user_router.get("/{user_uuid}", response_model=s.User)
def get_user_profile(
    user_uuid: str,
    db: Session = Depends(get_db),
):
    user: m.User = db.scalars(select(m.User).where(m.User.uuid == user_uuid)).first()
    if not user:
        log(
            log.ERROR,
            "User %s not found",
            user_uuid,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
