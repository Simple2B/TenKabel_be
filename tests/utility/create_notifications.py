import random

from sqlalchemy.orm import Session
from sqlalchemy import select
from faker import Faker

from app import model as m
from app import schema as s
from app.logger import log

fake: Faker = Faker()


def create_notifications(db: Session):
    users = db.scalars(select(m.User)).all()
    jobs_ids = db.scalars(select(m.Job.id)).all()
    applications_ids = db.scalars(select(m.Application.id)).all()

    for user in users:
        for _ in range(1, random.randint(1, 5)):
            type = random.choice([e for e in s.NotificationType])
            while type in (
                s.NotificationType.MAX_APPLICATION_TYPE,
                s.NotificationType.MAX_JOB_TYPE,
            ):
                type = random.choice([e for e in s.NotificationType])

            if s.NotificationType.get_index(type) < s.NotificationType.get_index(
                s.NotificationType.MAX_JOB_TYPE
            ):
                entity_id = random.choice(jobs_ids)

            elif s.NotificationType.get_index(type) < s.NotificationType.get_index(
                s.NotificationType.MAX_APPLICATION_TYPE
            ):
                entity_id = random.choice(applications_ids)

            notification = m.Notification(
                user_id=user.id,
                entity_id=entity_id,
                type=type,
            )
            db.add(notification)
    db.commit()

    log(log.INFO, "Notifications created - %s", db.query(m.Application).count())
