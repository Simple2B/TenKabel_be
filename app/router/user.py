from fastapi import HTTPException, Depends, APIRouter, status, File, UploadFile

from sqlalchemy import select
from sqlalchemy.orm import Session
from google.api_core.exceptions import GoogleAPICallError

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user, get_google_client
from app.database import get_db
from app.config import Settings, get_settings

user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    db: Session = Depends(get_db),
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


@user_router.post("/upload-avatar", status_code=status.HTTP_201_CREATED)
def upload_avatar(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    google_client=Depends(get_google_client),
    profile_avatar: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    file_path = f"{current_user.email}/images/avatar/{profile_avatar.filename}"
    with open(profile_avatar.filename, "wb") as f:
        f.write(profile_avatar.file.read())
        try:
            bucket = google_client.get_bucket(settings.GOOGLE_BUCKET_NAME)
            blob = bucket.blob(file_path)
            blob.upload_from_filename(file_path)
        except GoogleAPICallError as e:
            log(log.ERROR, "Error uploading file to google cloud storage: \n%s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request"
            )
    return status.HTTP_200_OK
