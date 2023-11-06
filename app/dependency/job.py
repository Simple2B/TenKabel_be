from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
import app.model as m
from app.logger import log
from . import get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_job_by_uuid(
    job_uuid: str,
    current_user: m.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> m.Job:
    job: m.Job | None = db.scalars(select(m.Job).where(m.Job.uuid == job_uuid)).first()
    if not job or job.is_deleted:
        log(log.INFO, "Job [%s] wasn`t found", job_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if current_user not in (job.worker, job.owner):
        log(log.INFO, "User [%s] is not related to job", job_uuid)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User not related",
        )

    return job


# def get_user(request: Request, db: Session = Depends(get_db)) -> m.User | None:
#     """Raises an exception if the current user is authenticated"""
#     auth_header: str = request.headers.get("Authorization")
#     if auth_header:
#         # Assuming the header value is in the format "Bearer <token>"
#         token: s.TokenData = verify_access_token(
#             auth_header.split(" ")[1], INVALID_CREDENTIALS_EXCEPTION
#         )
#         user = db.query(m.User).filter_by(id=token.user_id).first()
#         if user and not user.is_deleted:
#             return user
