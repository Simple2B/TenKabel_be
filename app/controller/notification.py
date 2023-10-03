from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app import model as m
from app import schema as s
from .push_notification import PushHandler
from app.utility.notification import get_notification_payload
from app.logger import log


def check_location_notification(regions: list[m.Location], user: m.User) -> bool:
    return user.notification_locations_flag and (
        (any(region in user.notification_locations for region in regions))
        or (
            not user.notification_locations
            and any(region in user.locations for region in regions)
        )
    )


def check_profession_notification(profession: m.Profession, user: m.User) -> bool:
    return user.notification_profession_flag and (
        (profession in user.notification_profession)
        or (not user.notification_profession and profession in user.professions)
    )


def job_created_notify(job: m.Job, db: Session) -> None:
    db.refresh(job)
    regions_ids: list[int] = [region.id for region in job.regions]
    profession: m.Profession = db.scalar(
        select(m.Profession).where(m.Profession.id == job.profession_id)
    )
    users: list[m.User] = db.scalars(
        select(m.User).where(
            and_(
                m.User.notification_locations.any(m.Location.id.in_(regions_ids)),
                m.User.notification_profession.contains(profession),
            )
        )
    ).all()
    users += db.scalars(
        select(m.User).where(
            and_(
                m.User.notification_locations.any(m.Location.id.in_(regions_ids)),
                ~m.User.notification_profession.any(),
            )
        )
    ).all()
    users += db.scalars(
        select(m.User).where(
            and_(
                ~m.User.notification_locations.any(),
                m.User.notification_profession.contains(profession),
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
            check_location_notification(regions_ids, user)
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
) -> None:
    if initial_job.status == job.status.value:
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
) -> None:
    if initial_job.payment_status == job.payment_status.value:
        log(log.DEBUG, "Job [%i] payment status not changed", job.id)
        return

    user = job.worker if current_user == job.owner else job.owner

    if not user or user.is_deleted:
        log(log.INFO, "User for notification not found")
        return

    notification_type = None
    if job.payment_status == s.enums.PaymentStatus.PAID:
        notification_type = s.NotificationType.JOB_PAID

    if job.payment_status == s.enums.PaymentStatus.REQUESTED:
        notification_type = s.NotificationType.PAYMENT_REQUESTED

    if job.payment_status == s.enums.PaymentStatus.DENY:
        notification_type = s.NotificationType.PAYMENT_DENIED

    if job.payment_status == s.enums.PaymentStatus.SENT:
        notification_type = s.NotificationType.PAYMENT_SENT

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


def handle_job_commission_notification(
    current_user: m.User, job: m.Job, db: Session, initial_job: s.Job
) -> None:
    if initial_job.commission_status == job.commission_status.value:
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

    if job.commission_status == s.enums.CommissionStatus.DENY:
        notification_type = s.NotificationType.COMMISSION_DENIED

    if job.commission_status == s.enums.CommissionStatus.SENT:
        notification_type = s.NotificationType.COMMISSION_SENT

    if not notification_type:
        log(log.INFO, "Job [%i] commission status not changed", job.id)
        return

    log(
        log.INFO,
        "Job [%i] commission status changed to [%s]",
        job.id,
        notification_type,
    )
    notification: m.Notification = m.Notification(
        user_id=user.id,
        entity_id=job.id,
        type=notification_type,
    )
    db.add(notification)

    if not user.notification_job_status:
        log(
            log.INFO,
            "User [%i] notification_commission_job_status is disabled",
            user.id,
        )
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
