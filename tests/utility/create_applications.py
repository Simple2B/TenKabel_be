import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake: Faker = Faker()


def create_applications(db: Session):
    worker_ids = [worker_id for worker_id in db.scalars(select(m.User.id)).all()]
    owner_ids = [owner_id for owner_id in db.scalars(select(m.Job.owner_id)).all()]
    job_ids = [job_id for job_id in db.scalars(select(m.Job.id)).all()]

    for job_id in range(len(job_ids)):
        for i in range(0, random.randint(0, 5)):
            worker_id = random.choice(worker_ids)
            owner_id = random.choice(owner_ids)
            while owner_id == worker_id:
                owner_id = random.choice(owner_ids)
            application = m.Application(
                job_id=job_id,
                owner_id=owner_id,
                worker_id=worker_id,
                created_at=fake.date_time_between(start_date="-30d", end_date="now"),
                status=random.choice(
                    [
                        s.BaseApplication.ApplicationStatus.DECLINED,
                        s.BaseApplication.ApplicationStatus.PENDING,
                    ]
                ),
            )
            db.add(application)
            db.commit()

    log(log.INFO, "Applications created - %s", db.query(m.Application).count())
