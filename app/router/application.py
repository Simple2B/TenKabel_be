from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.dependency import get_current_user, get_payplus_verified_user
from app.controller import PushHandler, create_application_payments
from app.utility.notification import get_notification_payload


application_router = APIRouter(prefix="/applications", tags=["Application"])


@application_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=s.ApplicationOut
)
def create_application(
    application_data: s.ApplicationIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_payplus_verified_user),
):
    job: m.Job = db.scalar(
        select(m.Job).where(
            and_(
                m.Job.id == application_data.job_id,
                m.Job.status == s.enums.JobStatus.PENDING,
            )
        )
    )
    if not job or job.is_deleted:
        log(log.INFO, "Job wasn`t found [%s]", application_data.job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    already_exist_application: m.Application = db.scalar(
        select(m.Application).where(
            and_(
                m.Application.job_id == application_data.job_id,
                m.Application.worker_id == current_user.id,
            )
        )
    )
    if already_exist_application:
        log(log.ERROR, "Application already exist")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already exist",
        )

    application: m.Application = m.Application(
        job_id=application_data.job_id,
        owner_id=job.owner_id,
        worker_id=current_user.id,
    )
    db.add(application)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new application - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error creating new application",
        )
    log(log.INFO, "Application created successfully - [%s]", application.id)
    db.refresh(application)

    user = job.worker if current_user == job.owner else job.owner

    if user:
        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=application.id,
            type=s.NotificationType.APPLICATION_CREATED,
        )
        db.add(notification)
        db.commit()

        push_handler = PushHandler()
        push_handler.send_notification(
            s.PushNotificationMessage(
                device_tokens=[device.push_token for device in user.devices],
                payload=get_notification_payload(
                    notification_type=notification.type,
                    job=job,
                    application=application,
                ),
            )
        )

    return s.ApplicationOut.from_orm(application)


@application_router.put(
    "/{uuid}", status_code=status.HTTP_201_CREATED, response_model=s.ApplicationOut
)
def update_application(
    uuid: str,
    application_data: s.BaseApplication,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    application: m.Application | None = db.scalar(
        select(m.Application).where(
            and_(
                m.Application.uuid == uuid,
            )
        )
    )
    if not application:
        log(log.INFO, "Application (with status pending) wasn`t found [%s]", uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application (with status pending) not found",
        )
    if application.worker_id == application.owner_id:
        log(log.INFO, "User can't send application to his job")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User can't send application to his job",
        )

    worker: m.User = db.scalar(select(m.User).where(m.User.id == application.worker_id))
    if not worker or worker.is_deleted:
        log(log.INFO, "User with id [%s] wasn`t found", application.worker_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    owner: m.User = db.scalar(select(m.User).where(m.User.id == application.owner_id))
    if not owner or owner.is_deleted:
        log(log.INFO, "User with id [%s] wasn`t found", application.owner_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    application.worker_id = application_data.worker_id
    application.owner_id = application_data.owner_id
    application.job_id = application_data.job_id

    application.status = s.Application.ApplicationStatus(application_data.status)
    job = application.job

    if application.status == s.BaseApplication.ApplicationStatus.ACCEPTED:
        pending_applications: list[m.Application] = db.scalars(
            select(m.Application).where(m.Application.job_id == application.job_id)
        ).all()
        for pending_application in pending_applications:
            if pending_application.worker_id != application.worker_id:
                pending_application.status = (
                    s.BaseApplication.ApplicationStatus.DECLINED
                )
                notification: m.Notification = m.Notification(
                    user_id=pending_application.worker.id,
                    entity_id=application.id,
                    type=s.NotificationType.APPLICATION_REJECTED,
                )
                db.add(notification)

                push_handler = PushHandler()
                push_handler.send_notification(
                    s.PushNotificationMessage(
                        device_tokens=[
                            device.push_token
                            for device in pending_application.worker.devices
                        ],
                        payload=get_notification_payload(
                            notification_type=notification.type, job=job
                        ),
                    )
                )
        log(log.INFO, "Applications to [%s] job updated", application.job_id)

        job.worker_id = application.worker_id
        job.status = s.enums.JobStatus.APPROVED
        create_application_payments(db, application)
        log(log.INFO, "Job [%s] status updated", job.id)
        notification_type = s.NotificationType.APPLICATION_ACCEPTED
    else:
        notification_type = s.NotificationType.APPLICATION_REJECTED

    user = application.worker if current_user == job.owner else job.owner

    if user:
        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=application.id,
            type=notification_type,
        )
        db.add(notification)
        push_handler = PushHandler()
        push_handler.send_notification(
            s.PushNotificationMessage(
                device_tokens=[device.push_token for device in user.devices],
                payload=get_notification_payload(
                    notification_type=notification.type, job=job
                ),
            )
        )

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating application - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating application"
        )

    log(log.INFO, "Application updated successfully - [%s]", application.id)
    return s.ApplicationOut.from_orm(application)


@application_router.patch(
    "/{uuid}", status_code=status.HTTP_201_CREATED, response_model=s.ApplicationOut
)
def patch_application(
    uuid: str,
    application_data: s.ApplicationPatch,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    application: m.Application | None = db.scalar(
        select(m.Application).where(
            and_(
                m.Application.uuid == uuid,
            )
        )
    )
    if not application:
        log(log.INFO, "Application (with status pending) wasn`t found [%s]", uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application (with status pending) not found",
        )
    if application.worker_id == application.owner_id:
        log(log.INFO, "User can't send application to his job")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User can't send application to his job",
        )

    worker: m.User = db.scalar(select(m.User).where(m.User.id == application.worker_id))
    if not worker or worker.is_deleted:
        log(log.INFO, "User with id [%s] wasn`t found", application.worker_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    owner: m.User = db.scalar(select(m.User).where(m.User.id == application.owner_id))
    if not owner or owner.is_deleted:
        log(log.INFO, "User with id [%s] wasn`t found", application.owner_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    if application_data.worker_id:
        application.worker_id = application_data.worker_id
    if application_data.owner_id:
        application.owner_id = application_data.owner_id
    if application_data.job_id:
        application.job_id = application_data.job_id
    if application_data.status:
        application.status = s.Application.ApplicationStatus(application_data.status)

    job = application.job

    if (
        s.Application.ApplicationStatus(application_data.status)
        == s.BaseApplication.ApplicationStatus.ACCEPTED
    ):
        pending_applications: list[m.Application] = db.scalars(
            select(m.Application).where(m.Application.job_id == application.job_id)
        ).all()
        for pending_application in pending_applications:
            if pending_application.worker_id != application.worker_id:
                pending_application.status = (
                    s.BaseApplication.ApplicationStatus.DECLINED
                )
                notification: m.Notification = m.Notification(
                    user_id=pending_application.worker.id,
                    entity_id=application.id,
                    type=s.NotificationType.APPLICATION_REJECTED,
                )
                db.add(notification)

                push_handler = PushHandler()
                push_handler.send_notification(
                    s.PushNotificationMessage(
                        device_tokens=[
                            device.push_token
                            for device in pending_application.worker.devices
                        ],
                        payload=get_notification_payload(
                            notification_type=notification.type, job=job
                        ),
                    )
                )
        log(log.INFO, "Applications to [%s] job updated", application.job_id)

        job.worker_id = application.worker_id
        job.status = s.enums.JobStatus.APPROVED
        create_application_payments(db, application)
        log(log.INFO, "Job [%s] status updated", job.id)
        notification_type = s.NotificationType.APPLICATION_ACCEPTED
    else:
        notification_type = s.NotificationType.APPLICATION_REJECTED

    user = application.worker if current_user == job.owner else job.owner

    if user:
        notification: m.Notification = m.Notification(
            user_id=user.id,
            entity_id=application.id,
            type=notification_type,
        )
        db.add(notification)

        push_handler = PushHandler()
        push_handler.send_notification(
            s.PushNotificationMessage(
                device_tokens=[device.push_token for device in user.devices],
                payload=get_notification_payload(
                    notification_type=notification.type, job=job
                ),
            )
        )

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while patching application - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error patching application"
        )

    log(log.INFO, "Application patched successfully - [%s]", application.id)
    return s.ApplicationOut.from_orm(application)
