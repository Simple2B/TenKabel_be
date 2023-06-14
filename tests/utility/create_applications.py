import random

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake: Faker = Faker()


def create_applications(db: Session):
    workers = db.scalars(select(m.User)).all()
    jobs = db.scalars(select(m.Job)).all()

    for job in jobs:
        for i in range(1, random.randint(1, 5)):
            worker = random.choice(workers)
            owner = db.scalar(select(m.Job).where(m.Job.id == job.id))

            while owner.id == worker.id:
                worker = random.choice(workers)

            application = m.Application(
                job_id=job.id,
                owner_id=owner.id,
                worker_id=worker.id,
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
    jobs: list[int] = db.scalars(
        select(m.Job).where(
            and_(m.Job.owner_id != user_id, m.Job.status == s.enums.Status.PENDING)
        )
    ).all()
    workers = db.scalars(select(m.User).where(m.User.id != user_id)).all()
    user_jobs: list[m.Job] = db.scalars(
        select(m.Job).where(
            and_(m.Job.owner_id == user_id, m.Job.status == s.enums.Status.PENDING)
        )
    ).all()

    for job in user_jobs:
        applications_count = 0
        for _ in range(3):
            worker = random.choice(workers)
            application: m.Application = m.Application(
                job_id=job.id,
                owner_id=job.owner_id,
                worker_id=worker.id,
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
        job = random.choice(jobs)
        owner = db.scalar(select(m.Job).where(m.Job.id == job.id))
        application: m.Application = m.Application(
            job_id=job.id,
            owner_id=owner.id,
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
