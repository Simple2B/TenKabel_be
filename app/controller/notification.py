from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app import model as m
from app import schema as s
from .push_notification import PushHandler
from app.utility.notification import get_notification_payload
from app.logger import log


def check_location_notification(region: m.Location, user: m.User):
    return user.notification_locations_flag and (
        (region in user.notification_locations)
        or (not user.notification_locations and region in user.locations)
    )


def check_profession_notification(profession: m.Profession, user: m.User):
    return user.notification_profession_flag and (
        (profession in user.notification_profession)
        or (not user.notification_profession and profession in user.professions)
    )


def job_created_notify(job: m.Job, db: Session):
    db.refresh(job)
    regions: m.Location = db.scalar(
        select(m.Location).where(m.Location.name_en == job.region)
    )
    profession: m.Profession = db.scalar(
        select(m.Profession).where(m.Profession.id == job.profession_id)
    )
    users: list[m.User] = db.scalars(
        select(m.User).where(
            and_(
                m.User.locations.contains(regions),
                m.User.professions.contains(profession),
            )
        )
    ).all()
    users += db.scalars(
        select(m.User).where(
            and_(
                m.User.locations.contains(regions),
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
        if user.is_deleted:
            continue

        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=job.id,
            type=s.NotificationType.JOB_CREATED,
        )
        db.add(notification)
        if (check_profession_notification(profession, user)) or (
            check_location_notification(regions, user)
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


def handle_job_status_update_notification(
    current_user: m.User, job: m.Job, db: Session, initial_job: s.Job
):
    if initial_job.status == job.status:
        log(log.DEBUG, "Job [%i] status not changed", job.id)
        return
    notification_type = None
    if job.status == s.enums.JobStatus.APPROVED:
        notification_type = s.NotificationType.JOB_STARTED

    if job.status == s.enums.JobStatus.JOB_IS_FINISHED:
        notification_type = s.NotificationType.JOB_DONE

    user = job.worker if current_user == job.owner else job.owner

    if notification_type and user and not user.is_deleted:
        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=job.id,
            type=notification_type,
        )
        db.add(notification)

        if user.notification_job_status:
            push_handler = PushHandler()
            push_handler.send_notification(
                s.PushNotificationMessage(
                    device_tokens=[device.push_token for device in user.devices],
                    payload=get_notification_payload(
                        notification_type=notification.type, job=job
                    ),
                )
            )


def handle_job_payment_notification(
    current_user: m.User, job: m.Job, db: Session, initial_job: s.Job
):
    if initial_job.payment_status == job.payment_status:
        log(log.DEBUG, "Job [%i] payment status not changed", job.id)
        return

    user = job.worker if current_user == job.owner else job.owner

    if not user or job.payment_status != s.enums.PaymentStatus.PAID or user.is_deleted:
        return

    notification: m.Notification = m.Notification(
        user_id=user.id,
        entity_id=job.id,
        type=s.NotificationType.JOB_PAID,
    )
    db.add(notification)

    if user.notification_job_status:
        push_handler = PushHandler()
        push_handler.send_notification(
            s.PushNotificationMessage(
                device_tokens=[device.push_token for device in user.devices],
                payload=get_notification_payload(
                    notification_type=notification.type, job=job
                ),
            )
        )


def handle_job_commission_notification(
    current_user: m.User, job: m.Job, db: Session, initial_job: s.Job
):
    if initial_job.commission_status == job.commission_status:
        log(log.DEBUG, "Job [%i] commission status not changed", job.id)
        return

    user = job.worker if current_user == job.owner else job.owner

    if not user or user.is_deleted:
        return

    notification_type = None
    if job.commission_status == s.enums.CommissionStatus.PAID:
        notification_type = s.NotificationType.COMMISSION_PAID

    if job.commission_status == s.enums.CommissionStatus.REQUESTED:
        notification_type = s.NotificationType.COMMISSION_REQUESTED

    if not notification_type:
        return

    notification: m.Notification = m.Notification(
        user_id=user.id,
        entity_id=job.id,
        type=notification_type,
    )
    db.add(notification)

    if not user.notification_job_status:
        return

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=[device.push_token for device in user.devices],
            payload=get_notification_payload(
                notification_type=notification.type, job=job
            ),
        )
    )
