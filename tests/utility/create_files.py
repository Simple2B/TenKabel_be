import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app.logger import log

from . import create_jobs

fake: Faker = Faker()


def create_files(db: Session, num_test_files: int = 150, is_create_jobs: bool = True):
    if is_create_jobs:
        create_jobs(db, 300)
    user_ids = [user.id for user in db.scalars(select(m.User)).all()]
    for _ in range(num_test_files):
        filename = fake.unique.file_name(category="image")
        file: m.File = m.File(
            user_id=random.choice(user_ids),
            url=fake.unique.image_url(),
            original_filename=filename,
        )
        db.add(file)
    db.commit()
    log(log.INFO, "Files created")


def create_files_for_user(db: Session, user_id: int, num_test_files=5, logs_off=False):
    for _ in range(num_test_files):
        filename = fake.unique.file_name(category="image")
        file: m.File = m.File(
            user_id=user_id,
            url=fake.unique.image_url(),
            original_filename=filename,
        )
        db.add(file)
    db.commit()
    if not logs_off:
        log(log.INFO, "Files for user [%s] created", user_id)
