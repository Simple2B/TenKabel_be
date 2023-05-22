import random
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake = Faker()


JOBS_LIST = [
    "mechanic",
    "courier",
    "medic",
    "deliveryman",
    "teacher",
    "handyman",
]


def create_jobs(db: Session):
    worker_ids = [worker.id for worker in db.scalars(select(m.User)).all()] + [None]

    profession_ids = [
        profession.id for profession in db.scalars(select(m.Profession)).all()
    ] + [None]
    for _ in range(len(worker_ids)):
        job: m.Job = m.Job(
            owner_id=random.choice(worker_ids[:-1]),
            worker_id=random.choice(worker_ids),
            profession_id=random.choice(profession_ids),
            name=random.choice(JOBS_LIST),
            description=fake.sentence(),
            status=random.choice([e for e in s.Job.Status]),
            payment=random.randint(0, 100),
            commission=random.uniform(0, 10),
            city=fake.city(),
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            payment_status=random.choice([e for e in s.Job.PaymentStatus]),
            commission_status=random.choice([e for e in s.Job.CommissionStatus]),
        )
        db.add(job)
        db.commit()
    log(log.INFO, "Jobs created - %s", db.query(m.Job).count())
