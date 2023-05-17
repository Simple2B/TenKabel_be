import random
from datetime import datetime

from invoke import task
from faker import Faker

from app.logger import log
import app.model as m
import app.schema as s


fake = Faker()


JOBS_LIST = [
    "mechanic",
    "courier",
    "medic",
    "deliveryman",
    "teacher",
    "handyman",
]


@task
def create_jobs(_):
    """Create a verified user for test"""

    from app.database import db

    with db.begin() as conn:
        worker_ids = [
            worker.id for worker in conn.scalars(conn.query(m.User)).all()
        ] + [None]

        profession_ids = [
            profession.id for profession in conn.query(m.Profession).all()
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
            conn.add(job)
        conn.commit()
    log(log.INFO, "Jobs created - %s", conn.query(m.Job).count())
