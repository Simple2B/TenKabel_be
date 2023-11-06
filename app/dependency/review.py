from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
import app.model as m
from app.logger import log

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_review_by_uuid(
    review_uuid: str,
    db: Session = Depends(get_db),
) -> m.Job:
    review: m.Review | None = db.scalar(
        select(m.Review).where(m.Review.uuid == review_uuid)
    )
    if not review:
        log(log.INFO, "Review [%s] wasn`t found", review_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    log(log.INFO, "Review [%s] info", review_uuid)
    return review
