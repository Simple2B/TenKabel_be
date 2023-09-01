import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log
from tests.utility import create_locations, create_professions, fill_test_data

from . import create_jobs

fake: Faker = Faker()


def create_attachments(
    db: Session, num_test_attachments: int = 150, is_create_jobs: bool = True
):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    if is_create_jobs:
        create_jobs(db, 300)
    job_ids = [job.id for job in db.scalars(select(m.Job)).all()] + [None]
    user_ids = [user.id for user in db.scalars(select(m.User)).all()]
    for _ in range(num_test_attachments):
        filename = fake.unique.file_name(category="image")
        attachment: m.Attachment = m.Attachment(
            job_id=random.choice(job_ids),
            created_by_id=random.choice(user_ids),
            type=random.choice(
                [s.enums.AttachmentType.DOCUMENT, s.enums.AttachmentType.IMAGE]
            ),
            url=fake.unique.image_url(),
            filename=filename,
            original_filename=filename,
            storage_path="attachments/" + filename,
            extension=filename.split(".")[-1],
        )
        db.add(attachment)
    db.commit()
    log(log.INFO, "Attachments created")
