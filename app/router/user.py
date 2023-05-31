import io

from fastapi import HTTPException, Depends, APIRouter, status, File, UploadFile, Form
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from google.api_core.exceptions import GoogleAPIError

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user, get_google_client
from app.database import get_db
from app.config import Settings, get_settings
from app.hash_utils import hash_verify


user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    current_user: m.User = Depends(get_current_user),
):
    return current_user


@user_router.put("", status_code=status.HTTP_200_OK)
def update_user(
    email: str = Form(None),
    username: str = Form(None),
    phone: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    professions: list[int] = Form(None),
    google_client=Depends(get_google_client),
    profile_avatar: UploadFile | None = File(None),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    if email:
        current_user.email = email
    if username:
        current_user.username = username
    if phone:
        current_user.phone = phone
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if profile_avatar:
        with open(profile_avatar.filename, "rb") as f:
            try:
                bucket = google_client.get_bucket(settings.GOOGLE_BUCKET_NAME)
                file_object = io.BytesIO(f.read())
                blob = bucket.blob(
                    f"images/avatars/{current_user.email}/{profile_avatar.filename}"
                )
                blob.upload_from_file(file_object)
            except GoogleAPIError as e:
                log(log.ERROR, "Error uploading file to google cloud storage: \n%s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"
                )
        current_user.picture = blob.public_url
    if professions:
        for profession in current_user.professions:
            db.delete(profession)
            db.flush()
        for profession_id in professions:
            profession = db.scalar(
                select(m.Profession).where(m.Profession.id == profession_id)
            )
            user_profession = db.scalar(
                select(m.UserProfession).where(
                    m.UserProfession.user_id == current_user.id,
                    m.UserProfession.profession_id == profession_id,
                )
            )
            if not user_profession:
                db.add(
                    m.UserProfession(
                        user_id=current_user.id, profession_id=profession_id
                    )
                )
                db.flush()
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating user"
        )

    log(log.INFO, "User updated successfully - %s", current_user.username)
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


@user_router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password: str,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    current_user.password = password

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user password - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating password"
        )

    log(log.INFO, "User password updated successfully - %s", current_user.username)
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


@user_router.get("/rates", status_code=status.HTTP_200_OK, response_model=s.RateList)
def get_user_rates(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    rates: s.RateList = db.scalars(
        select(m.Rate).where(m.Rate.worker_id == current_user.id)
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
