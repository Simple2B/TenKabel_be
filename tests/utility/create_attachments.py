from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from faker import Faker

from app import model as m
from app.logger import log

from .create_files import create_files_for_user
from .create_jobs import create_jobs_for_user

fake: Faker = Faker()


def create_attachments(db: Session, num_test_attachments: int = 150):
    users = db.scalars(select(m.User)).all()
    for user in users:
        create_jobs_for_user(db, user.id, 1, logs_off=True)
        create_files_for_user(db, user.id, 1, logs_off=True)
        job_id = db.scalars(select(m.Job.id).where(m.Job.owner_id == user.id)).first()
        file = db.scalars(select(m.File).where(m.File.user_id == user.id)).first()

        attachment: m.Attachment = m.Attachment(
            user_id=user.id,
            job_id=job_id,
            file_id=file.id,
        )
        db.add(attachment)
    db.commit()
    log(log.INFO, "Attachments created")


def create_attachments_for_user(
    db: Session, user_id: int, num_test_attachments: int = 2
):
    user = db.scalar(select(m.User).where(m.User.id == user_id))
    if not user:
        log(log.INFO, f"User with id {user_id} not found")
        return

    jobs = db.scalars(
        select(m.Job).where(or_(m.Job.owner_id == user_id, m.Job.worker_id == user_id))
    ).all()
    for job in jobs:
        create_files_for_user(db, user.id, 1, logs_off=True)
        file = db.scalars(select(m.File).where(m.File.user_id == user.id)).all()[-1]
        attachment: m.Attachment = m.Attachment(
            user_id=user.id,
            job_id=job.id,
            file_id=file.id,
        )
        db.add(attachment)
    db.commit()
    log(log.INFO, f"Attachments created for user {user_id}")
