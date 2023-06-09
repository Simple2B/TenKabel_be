import random

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
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
            owner_id = db.scalar(select(m.Job.owner_id).where(m.Job.id == job_id))

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


def create_applications_for_user(db: Session, user_id: int) -> None:
    job_ids: list[int] = db.scalars(
        select(m.Job.id).where(
            and_(m.Job.owner_id != user_id, m.Job.status == s.Job.Status.PENDING)
        )
    ).all()
    worker_ids = db.scalars(select(m.User.id).where(m.User.id != user_id)).all()
    user_jobs: list[m.Job] = db.scalars(
        select(m.Job.id).where(
            and_(m.Job.owner_id == user_id, m.Job.status == s.Job.Status.PENDING)
        )
    ).all()

    for job in user_jobs:
        applications_count = 0
        for _ in range(3):
            application: m.Application = m.Application(
                job_id=job.id,
                owner_id=job.owner_id,
                worker_id=random.choice(worker_ids),
                created_at=fake.date_time_between(start_date="-30d", end_date="now"),
                status=s.BaseApplication.ApplicationStatus.PENDING,
            )
            db.add(application)
            db.commit()
            applications_count += 1

        log(
            log.INFO,
            "Applications created for job (id)=[%s] as worker - %s",
            job.id,
            applications_count,
        )

    worker_jobs_count = 0
    for _ in range(3):
        job_id = random.choice(job_ids)
        owner_id = db.scalar(select(m.Job.owner_id).where(m.Job.id == job_id))
        application: m.Application = m.Application(
            job_id=job_id,
            owner_id=owner_id,
            worker_id=user_id,
            created_at=fake.date_time_between(start_date="-30d", end_date="now"),
            status=s.BaseApplication.ApplicationStatus.PENDING,
        )
        db.add(application)
        db.commit()
        worker_jobs_count += 1

    log(
        log.INFO,
        "Applications created for user (id)=[%s] as worker - %s",
        user_id,
        worker_jobs_count,
    )
