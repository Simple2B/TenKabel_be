from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app import model as m
from app import schema as s
from .push_notification import PushHandler
from app.utility.notification import get_notification_payload
from app.logger import log


def check_location_notification(city: m.Location, user: m.User):
    if user.notification_locations_flag is False:
        return False
    return (city in user.notification_locations) or (
        not user.notification_locations and city in user.locations
    )


def check_profession_notification(profession: m.Profession, user: m.User):
    if user.notification_profession_flag is False:
        return False
    return (profession in user.notification_profession) or (
        not user.notification_profession and profession in user.professions
    )


def job_created_notify(job: m.Job, db: Session):
    db.refresh(job)
    city: m.Location = db.scalar(
        select(m.Location).where(m.Location.name_en == job.city)
    )
    profession: m.Profession = db.scalar(
        select(m.Profession).where(m.Profession.id == job.profession_id)
    )
    users: list[m.User] = db.scalars(
        select(m.User).where(
            and_(
                m.User.locations.contains(city),
                m.User.professions.contains(profession),
            )
        )
    ).all()
    users += db.scalars(
        select(m.User).where(
            and_(
                m.User.locations.contains(city),
                ~m.User.professions.any(),
            )
        )
    ).all()
    users += db.scalars(
        select(m.User).where(
            and_(
                ~m.User.locations.any(),
                m.User.professions.contains(profession),
            )
        )
    ).all()

    devices: list[str] = list()
    for user in users:
        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=job.id,
            type=s.NotificationType.JOB_CREATED,
        )
        db.add(notification)
        if (check_profession_notification(profession, user)) or (
            check_location_notification(city, user)
        ):
            for device in user.devices:
                devices.append(device.push_token)

    db.commit()

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=devices,
            payload=get_notification_payload(
                notification_type=s.NotificationType.JOB_CREATED, job=job
            ),
        )
    )

    log(log.INFO, "[%d] notifications created", len(users))
    log(log.INFO, "[%d] notifications sended", len(devices))
