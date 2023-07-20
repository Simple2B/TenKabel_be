import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, or_, and_

from app.logger import log
from app import schema as s
from app import model as m


def manage_tab_controller(
    db: Session, current_user: m.User, query: select, manage_tab: s.Job.TabFilter
):
    try:
        manage_tab: s.Job.TabFilter = s.Job.TabFilter(manage_tab)
        log(log.INFO, "s.Job.TabFilter parameter: (%s)", manage_tab.value)
    except ValueError:
        log(log.INFO, "Filter manage tab doesn't exist - %s", manage_tab)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wrong filter")
    if manage_tab == s.Job.TabFilter.PENDING:
        log(
            log.INFO,
            "Pending tab, getting jobs ids for user: (%d)",
            current_user.id,
        )
        jobs_ids = db.scalars(
            select(m.Application.job_id).where(
                or_(
                    m.Application.worker_id == current_user.id,
                )
            )
        ).all()
        query = select(m.Job).filter(
            and_(
                or_(m.Job.id.in_(jobs_ids), m.Job.owner_id == current_user.id),
                m.Job.status == s.enums.JobStatus.PENDING,
                m.Job.is_deleted == False,  # noqa E712
            )
        )

        log(log.INFO, "Jobs filtered by ids: (%s)", ",".join(map(str, jobs_ids)))

    if manage_tab == s.Job.TabFilter.ACTIVE:
        query = query.where(
            and_(
                m.Job.is_deleted == False,  # noqa E712
                or_(
                    m.Job.payment_status == s.enums.PaymentStatus.UNPAID,
                    m.Job.commission_status == s.enums.CommissionStatus.UNPAID,
                ),
                m.Job.status.in_(
                    [s.enums.JobStatus.IN_PROGRESS, s.enums.JobStatus.JOB_IS_FINISHED]
                ),
            )
        )
        log(log.INFO, "Jobs filtered by status: %s", manage_tab)

    if manage_tab == s.Job.TabFilter.ARCHIVE:
        query = query.filter(
            or_(
                m.Job.is_deleted == True,  # noqa E712
                and_(
                    m.Job.payment_status == s.enums.PaymentStatus.PAID,
                    m.Job.commission_status == s.enums.CommissionStatus.PAID,
                    m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED,
                ),
            )
        )
        log(log.INFO, "Jobs filtered by status: %s", manage_tab)

    return query


def delete_device(
    device: s.LogoutIn,
    db: Session,
):
    device_from_db: m.Device | None = db.scalar(
        select(m.Device).where(m.Device.uuid == device.device_uuid)
    )

    if not device_from_db:
        log(log.ERROR, "Device [%s] was not found", device.device_uuid)
        return

    db.delete(device_from_db)
    db.commit()

    log(log.INFO, "Device [%s] was deleted", device_from_db.uuid)


def validate_user(user: m.User):
    errors = []
    for job in user.jobs_owned + user.jobs_to_do:
        if job.status == s.enums.JobStatus.IN_PROGRESS:
            errors.append("Job [%s] is in progress" % job.name)
        if job.status == s.enums.JobStatus.JOB_IS_FINISHED:
            if (
                job.payment_status == s.enums.PaymentStatus.UNPAID
                or job.commission_status == s.enums.CommissionStatus.UNPAID
            ):
                errors.append("Job [%s] is finished but not paid" % job.name)
    for platform_payment in user.platform_payments:
        if platform_payment.status != s.enums.PlatformPaymentStatus.PAID:
            errors.append("\n Payment platform not paid. Wait for processing")
    if errors:
        log(log.ERROR, "User [%s] can't be deleted - %s", user.id, errors)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User can't be deleted: {', '.join(errors)}",
        )


def delete_user_view(device: s.LogoutIn, current_user: m.User, db: Session):
    validate_user(current_user)

    delete_device(device, db)
    current_user.is_deleted = True
    current_user.username += f'%{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
    current_user.email += f'%{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
    if current_user.phone:
        current_user.phone += f'%{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'

    for job in current_user.jobs_owned + current_user.jobs_to_do:
        job.is_deleted = True
        if job.title:
            job.title += f'%{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'

    applications = db.scalars(
        select(m.Application).where(
            and_(
                or_(
                    m.Application.worker_id == current_user.id,
                    m.Application.owner_id == current_user.id,
                ),
                m.Application.status == s.BaseApplication.ApplicationStatus.PENDING,
            )
        )
    ).all()

    for application in applications:
        application.status = s.BaseApplication.ApplicationStatus.DECLINED

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while deleting user [%s] - %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error deleting user"
        )
    log(log.INFO, "User [%s] deleted successfully", current_user.id)
    return current_user
