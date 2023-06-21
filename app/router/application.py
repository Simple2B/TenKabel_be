from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.dependency import get_current_user
from app.controller import PushHandler


application_router = APIRouter(prefix="/application", tags=["Application"])


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
            m.Application.uuid == uuid
            and m.Application.status == s.BaseApplication.ApplicationStatus.PENDING
        )
    )
    if not application:
        log(log.INFO, "Application (with status pending) wasn`t found [%s]", uuid)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application (with status pending) not found",
        )
    if application.worker_id == application.owner_id:
        log(log.INFO, "User can't send application to his job")
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User can't send application to his job",
        )

    worker: m.User = db.scalar(select(m.User).where(m.User.id == application.worker_id))
    if not worker:
        log(log.INFO, "User with id [%s] wasn`t found", application.worker_id)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    owner: m.User = db.scalar(select(m.User).where(m.User.id == application.owner_id))
    if not owner:
        log(log.INFO, "User with id [%s] wasn`t found", application.owner_id)
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    application.worker_id = application_data.worker_id
    application.owner_id = application_data.owner_id
    application.job_id = application_data.job_id

    application.status = s.Application.ApplicationStatus(application_data.status)
    if application.status == s.BaseApplication.ApplicationStatus.ACCEPTED:
        pending_applications: list[m.Application] = db.scalars(
            select(m.Application).where(m.Application.job_id == application.job_id)
        ).all()
        for pending_application in pending_applications:
            if pending_application.worker_id != application.worker_id:
                pending_application.status = (
                    s.BaseApplication.ApplicationStatus.DECLINED
                )
        log(log.INFO, "Applications to [%s] job updated", application.job_id)

        job: m.Job = db.scalar(select(m.Job).where(m.Job.id == application.job_id))
        job.worker_id = application.worker_id
        job.status = s.enums.JobStatus.IN_PROGRESS
        log(log.INFO, "Job [%s] status updated", job.id)
        notification_type = s.NotificationType.APPLICATION_ACCEPTED
    else:
        notification_type = s.NotificationType.APPLICATION_REJECTED

    notification: m.Notification = m.Notification(
        user_id=current_user.id,
        entity_id=application.id,
        type=notification_type,
    )
    db.add(notification)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating application - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating application"
        )

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=[device.push_token for device in current_user.devices],
            payload=s.PushNotificationPayload(
                notification_type=notification.type,
                job_uuid=application.job_uuid,
            ),
        )
    )

    log(
        log.INFO,
        "Notification sended successfully to (worker) user [%s]",
        worker.first_name,
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
            m.Application.uuid == uuid
            and m.Application.status == s.BaseApplication.ApplicationStatus.PENDING
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
    if not worker:
        log(log.INFO, "User with id [%s] wasn`t found", application.worker_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn`t found",
        )

    owner: m.User = db.scalar(select(m.User).where(m.User.id == application.owner_id))
    if not owner:
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
        log(log.INFO, "Applications to [%s] job updated", application.job_id)

        job: m.Job = db.scalar(select(m.Job).where(m.Job.id == application.job_id))
        job.worker_id = application.worker_id
        job.status = s.enums.JobStatus.IN_PROGRESS
        log(log.INFO, "Job [%s] status updated", job.id)
        notification_type = s.NotificationType.APPLICATION_ACCEPTED
    else:
        notification_type = s.NotificationType.APPLICATION_REJECTED

    notification: m.Notification = m.Notification(
        user_id=current_user.id,
        entity_id=application.id,
        type=notification_type,
    )
    db.add(notification)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while patching application - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error patching application"
        )

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=[device.push_token for device in current_user.devices],
            payload=s.PushNotificationPayload(
                notification_type=notification.type,
                job_uuid=application.job_uuid,
            ),
        )
    )

    log(
        log.INFO,
        "Notification sended successfully to (worker) user [%s]",
        worker.first_name,
    )
    log(log.INFO, "Application patched successfully - [%s]", application.id)
    return s.ApplicationOut.from_orm(application)


@application_router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=s.ApplicationOut
)
def create_application(
    application_data: s.ApplicationIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    job: m.Job = db.scalar(
        select(m.Job).where(
            (m.Job.id == application_data.job_id)
            and (m.Job.status == s.enums.JobStatus.PENDING)
        )
    )
    if not job:
        log(log.INFO, "Job wasn`t found [%s]", application_data.job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    already_exist_application: m.Application = db.scalar(
        select(m.Application).where(
            (m.Application.job_id == application_data.job_id)
            and (m.Application.worker_id == current_user.id)
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

    notification: m.Notification = m.Notification(
        user_id=job.owner_id,
        entity_id=application.id,
        type=s.NotificationType.APPLICATION_CREATED,
    )
    db.add(notification)

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=[device.push_token for device in current_user.devices],
            payload=s.PushNotificationPayload(
                notification_type=notification.type,
                job_uuid=job.uuid,
            ),
        )
    )

    log(
        log.INFO,
        "Notification sended successfully to (owner) user [%s]",
        job.owner_id,
    )

    return s.ApplicationOut.from_orm(application)
