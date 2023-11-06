from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.logger import log
from app.dependency import get_current_user
import app.schema as s
import app.model as m

app_review_router = APIRouter(prefix="/app-review", tags=["App Reviews"])


@app_review_router.get(
    "/{review_uuid}",
    response_model=s.AppReviewOut,
    status_code=status.HTTP_200_OK,
)
def get_app_review(
    review_uuid: str,
    db: Session = Depends(get_db),
):
    app_review = db.scalar(select(m.AppReview).where(m.AppReview.uuid == review_uuid))
    if not app_review:
        log(log.INFO, "App review [%s] not found", review_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App review not found",
        )
    return app_review


@app_review_router.post(
    "",
    response_model=s.AppReviewOut,
    status_code=status.HTTP_201_CREATED,
)
def create_app_review(
    app_review: s.AppReviewIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    app_review = m.AppReview(
        user_id=current_user.id,
        stars_count=app_review.stars_count,
        review=app_review.review,
    )
    db.add(app_review)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Failed to create app review: %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to create app review",
        )
    log(log.INFO, "App review [%s] was created", app_review.uuid)
    return app_review
