import random
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake: Faker = Faker()


JOBS_LIST = [
    "mechanic",
    "courier",
    "medic",
    "deliveryman",
    "teacher",
    "handyman",
]

TEST_CITIES = [
    "Afula",
    "Akko",
    "Arad",
    "Ariel",
    "Ashdod",
    "Ashkelon",
    "Ashkelon",
    "Baqa al-Gharbiyye",
    "Bat Yam",
    "Beer Sheva",
    "Beit Shean",
    "Beit Shemesh",
    "Betar Illit",
    "Bnei Berak",
    "Dimona",
    "Eilat",
    "Elad",
    "Givatayim",
]


def create_jobs(db: Session, test_jobs_num: int = 100):
    worker_ids = [worker.id for worker in db.scalars(select(m.User)).all()] + [None]

    profession_ids = [
        profession.id for profession in db.scalars(select(m.Profession)).all()
    ]
    for _ in range(test_jobs_num):
        job: m.Job = m.Job(
            owner_id=random.choice(worker_ids[:-1]),
            worker_id=random.choice(worker_ids),
            profession_id=random.choice(profession_ids),
            name=random.choice(JOBS_LIST),
            description=fake.sentence(),
            status=random.choice([e for e in s.Job.Status]),
            payment=random.randint(0, 100),
            commission=random.uniform(0, 10),
            city=random.choice(TEST_CITIES),
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            payment_status=random.choice([e for e in s.Job.PaymentStatus]),
            commission_status=random.choice([e for e in s.Job.CommissionStatus]),
            who_pays=random.choice([e for e in s.Job.WhoPays]),
            customer_first_name=fake.first_name(),
            customer_last_name=fake.last_name(),
            customer_phone=fake.phone_number(),
            customer_street_address=fake.address(),
        )
        db.add(job)
        db.commit()

    # owner can't work on his own job
    for job in db.query(m.Job).all():
        while job.owner_id == job.worker_id:
            job.worker_id = random.choice(worker_ids)

        db.commit()
    log(log.INFO, "Jobs created - %s", test_jobs_num)
