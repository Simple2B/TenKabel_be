import random

from sqlalchemy.orm import Session
from sqlalchemy import select

from app import schema as s
from app import model as m
from app.logger import log


NUM_TEST_USERS = 100
MAX_RATES_NUM = 5


def create_rates(db: Session):
    rates_num_total = 0

    for user in db.scalars(select(m.User)).all():
        rates_num_total += len(user.jobs_owned)
        for job in user.jobs_owned:
            if job.status == s.JobStatus.JOB_IS_FINISHED and not db.scalar(
                select(m.Rate).where(m.Rate.job_id == job.id)
            ):
                rate = m.Rate(
                    job_id=job.id,
                    worker_id=user.id,
                    owner_id=job.worker_id,
                    rate=random.choice([e for e in s.BaseRate.RateStatus]),
                )
                db.add(rate)
                rate = m.Rate(
                    job_id=job.id,
                    worker_id=job.worker_id,
                    owner_id=user.id,
                    rate=random.choice([e for e in s.BaseRate.RateStatus]),
                )
                db.add(rate)
        db.flush()
    db.commit()
    log(log.INFO, "Rates created - %s", rates_num_total)
