import random

from sqlalchemy.orm import Session
from sqlalchemy import select

from app import schema as s
from app import model as m
from app.logger import log


TAGS_WORDS = [
    "Good",
    "Well",
    "Nice",
    "Great",
    "Awesome",
    "Amazing",
    "Fantastic",
    "Wonderful",
    "Perfect",
    "Awful",
    "Bad",
    "Terrible",
    "Horrible",
    "Unacceptable",
    "Unsatisfactory",
]


def create_reviews(db: Session):
    reviews_num_total = 0

    if not db.scalar(select(m.Tag)):
        for tag in TAGS_WORDS:
            db.add(m.Tag(tag=tag, rate=s.BaseRate.RateStatus.POSITIVE))
        db.flush()

    tags = db.scalars(select(m.Tag)).all()
    for user in db.scalars(select(m.User)).all():
        reviews_num_total += len(user.jobs_owned)
        for job in user.jobs_owned:
            if job.status == s.JobStatus.JOB_IS_FINISHED and not db.scalar(
                select(m.Review).where(m.Review.job_id == job.id)
            ):
                review = m.Review(
                    job_id=job.id,
                    evaluates_id=user.id,
                    evaluated_id=job.worker_id,
                    rate=random.choice([e for e in s.BaseRate.RateStatus]),
                    tag=random.choice(tags),
                )
                db.add(review)
                review = m.Review(
                    job_id=job.id,
                    evaluates_id=job.worker_id,
                    evaluated_id=user.id,
                    rate=random.choice([e for e in s.BaseRate.RateStatus]),
                    tag=random.choice(tags),
                )
                db.add(review)
        db.flush()
    db.commit()
    log(log.INFO, "Reviews created - %s", reviews_num_total)
