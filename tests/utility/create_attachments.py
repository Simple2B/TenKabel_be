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


def create_attachments(db: Session, num_test_attachments: int = 25):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    create_jobs(db, 300)
    job_ids = [job.id for job in db.scalars(select(m.Job)).all()] + [None]
    for _ in range(num_test_attachments):
        filename = fake.unique.file_name(category="image")
        attachment: m.Attachment = m.Attachment(
            job_id=random.choice(job_ids),
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
