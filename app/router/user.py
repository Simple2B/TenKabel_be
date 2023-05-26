from fastapi import HTTPException, Depends, APIRouter, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user
from app.database import get_db
from app.hash_utils import hash_verify


user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    return current_user


@user_router.put("", status_code=status.HTTP_200_OK)
def update_user(
    user_data: s.User,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    user: m.User | None = db.scalars(
        select(m.User).where(m.User.uuid == current_user.uuid)
    ).first()
    if not user:
        log(log.INFO, "User wasn`t found %s", current_user.uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user_data.email != user.email:
        user.email = user_data.email
    if user_data.username != user.username:
        user.username = user_data.username
    user.google_openid_key = user_data.google_openid_key
    user.picture = user_data.picture
    user.created_at = user_data.created_at
    user.is_verified = user_data.is_verified
    if user_data.phone != user.phone:
        user.phone = user_data.phone
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    if user_data.professions != user.professions:
        user.professions = user_data.professions

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updatin user - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating user"
        )

    log(log.INFO, "User updated successfully - %s", user.username)
    return status.HTTP_200_OK


@user_router.post("/check-password", status_code=status.HTTP_200_OK)
def check_password(
    password: str,
    current_user: m.User = Depends(get_current_user),
):
    if not hash_verify(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Password does not match"
        )
    return status.HTTP_200_OK


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
