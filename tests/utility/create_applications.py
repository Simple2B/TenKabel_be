import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake: Faker = Faker()


def create_applications(db: Session):
    worker_ids = db.scalars(select(m.User.id)).all()
    job_ids = db.scalars(select(m.Job.id)).all()

    for job_id in job_ids:
        for i in range(1, random.randint(1, 5)):
            worker_id = random.choice(worker_ids)
            owner_id = db.scalar(select(m.Job.id).where(m.Job.id == job_id))

            while owner_id == worker_id:
                worker_id = random.choice(worker_ids)
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
