from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.dependency import get_current_user, get_review_by_uuid


review_router = APIRouter(prefix="/reviews", tags=["Review"])


@review_router.get(
    "/{review_uuid}", status_code=status.HTTP_200_OK, response_model=s.ReviewOut
)
def get_review(
    review_uuid: str,
    db: Session = Depends(get_db),
    review: m.Review = Depends(get_review_by_uuid),
):
    return s.ReviewOut(
        evaluated_id=review.evaluated_id,
        evaluates_id=review.evaluates_id,
        job_uuid=review.job.uuid,
        tag=s.TagOut(
            rate=review.tag.rate,
            tag=review.tag.tag,
        ),
    )


@review_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=s.ReviewsOut
)
def create_reviews(
    review_data: s.ReviewIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    evaluated: m.User | None = db.scalar(
        select(m.User).where(m.User.id == review_data.evaluated_id)
    )
    if not evaluated or evaluated.is_deleted:
        log(log.INFO, "Evaluated [%s] wasn`t found ", review_data.evaluated_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evaluated not found",
        )

    evaluates: m.User | None = db.scalar(
        select(m.User).where(m.User.id == review_data.evaluates_id)
    )
    if not evaluates or evaluates.is_deleted:
        log(log.INFO, "Evaluates [%s] wasn`t found ", review_data.evaluates_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Evaluates not found",
        )
    job = db.scalar(select(m.Job).where(m.Job.uuid == review_data.job_uuid))
    if not job:
        log(log.INFO, "Job [%s] wasn`t found ", review_data.job_uuid)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job not found",
        )
    if current_user not in (evaluated, evaluates):
        log(log.INFO, "User [%s] is not related to review", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User not related",
        )

    if evaluated not in (job.worker, job.owner) or evaluates not in (
        job.worker,
        job.owner,
    ):
        log(log.INFO, "Users [%s] or [%s] are not related to job", evaluated, evaluates)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Users not related",
        )

    if job.status != s.enums.JobStatus.JOB_IS_FINISHED:
        log(log.INFO, "Job [%s] is not completed", job.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is not completed",
        )

    rates = []
    for rate in review_data.rates:
        for tag_in in rate.tags:
            tag = db.scalar(
                select(m.Tag).where(
                    and_(
                        m.Tag.tag == tag_in,
                        # m.Tag.profession_id == job.profession_id,
                        m.Tag.rate == rate.rate,
                    )
                )
            )
            if not tag:
                log(
                    log.INFO,
                    "Creating tag [%s] - [%s] ",
                    tag_in,
                    rate.rate,
                )
                # tag = m.Tag(tag=tag_in, profession_id=job.profession_id, rate=rate.rate)
                tag = m.Tag(tag=tag_in, rate=rate.rate)
                db.add(tag)
                db.commit()

            review = m.Review(
                evaluated_id=review_data.evaluated_id,
                evaluates_id=review_data.evaluates_id,
                job_id=job.id,
                tag_id=tag.id,
                rate=rate.rate,
            )
            db.add(review)
            db.commit()
            rates.append(tag)
        log(
            log.INFO,
            "Reviews with [%s] created (%s) successfully",
            rate.rate,
            len(rate.tags),
        )
    log(log.INFO, "Reviews (%s) -> (%s) created successfully", evaluates, evaluated)
    return s.ReviewsOut(
        evaluated_id=review_data.evaluated_id,
        evaluates_id=review_data.evaluates_id,
        job_uuid=review_data.job_uuid,
        tags=rates,
    )
