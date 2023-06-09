from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.controller.notification import (
    handle_job_commission_notification,
    handle_job_payment_notification,
    handle_job_status_update_notification,
)

from app.dependency import (
    get_current_user,
    get_user,
    get_job_by_uuid,
    get_payplus_verified_user,
)
from app.exceptions import ValueDownGradeForbidden
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.utility import time_measurement
from app.utility.get_pending_jobs_query import get_pending_jobs_query_for_user
from app.controller import PushHandler, job_created_notify
from app.utility.notification import get_notification_payload


job_router = APIRouter(prefix="/job", tags=["Jobs"])


@job_router.get(
    "/status_list", status_code=status.HTTP_200_OK, response_model=list[str]
)
def get_status_list():
    return [e.value for e in s.enums.JobStatus]


@job_router.get("/jobs", status_code=status.HTTP_200_OK, response_model=s.ListJob)
@time_measurement
def get_jobs(
    profession_id: int = None,
    city: str = None,
    min_price: int = None,
    max_price: int = None,
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_user),
    q: str | None = "",
) -> s.ListJob:
    query = get_pending_jobs_query_for_user(db, user)

    if q:
        query = query.where(
            or_(
                m.Job.name.icontains(f"%{q}%"),
                m.Job.description.icontains(f"%{q}%"),
                m.Job.city.icontains(f"%{q}%"),
            )
        )
        log(log.INFO, "Job filtered by [%s] containing", q)

    elif (
        user is None
        or user.google_openid_key
        or any([profession_id, city, min_price, max_price])
    ):
        if profession_id:
            query = query.where(m.Job.profession_id == profession_id)
        if city:
            # city = re.sub(r"[^a-zA-Z0-9]", "", city)
            query = query.where(m.Job.city.ilike(f"%{city}%"))
        if min_price:
            query = query.where(m.Job.payment >= min_price)
        if max_price:
            query = query.where(m.Job.payment <= max_price)
        log(log.INFO, "Job filtered")
    else:
        profession_ids: list[int] = [profession.id for profession in user.professions]
        cities_names: list[str] = [location.name_en for location in user.locations]
        if profession_ids:
            filter_conditions = []
            for prof_id in profession_ids:
                filter_conditions.append(m.Job.profession_id == prof_id)
            query = query.filter(or_(*filter_conditions))

            log(
                log.INFO,
                "Job filtered by profession ids [%s] user interests",
                profession_ids,
            )
        if cities_names:
            filter_conditions = []
            for location in cities_names:
                filter_conditions.append(m.Job.city.ilike(location))
            query = query.filter(or_(*filter_conditions))
            log(
                log.INFO,
                "Job filtered by cities names [%s] user interests",
                ",".join(cities_names),
            )
        if not cities_names and not profession_ids:
            log(log.INFO, "Job returned with no filters")

    jobs: s.ListJob = s.ListJob(jobs=db.scalars(query.order_by(m.Job.id)).all())
    log(log.INFO, "Job [%s] at all got", len(jobs.jobs))
    return jobs


@job_router.get("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def get_job(
    job_uuid: str,
    db: Session = Depends(get_db),
) -> s.Job:
    job: m.Job | None = db.scalars(select(m.Job).where(m.Job.uuid == job_uuid)).first()
    if not job:
        log(log.INFO, "Job wasn`t found [%s]", job_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    log(log.INFO, "Job [%s] info", job_uuid)
    return job


@job_router.post("", status_code=status.HTTP_201_CREATED, response_model=s.Job)
def create_job(
    data: s.JobIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_payplus_verified_user),
):
    if data.who_pays:
        who_pays = s.Job.WhoPays(data.who_pays)

    new_job = m.Job(
        owner_id=current_user.id,
        profession_id=data.profession_id,
        name=data.name,
        description=data.description,
        payment=data.payment,
        commission=data.commission,
        who_pays=who_pays,
        city=data.city,
        time=data.time,
        customer_first_name=data.customer_first_name,
        customer_last_name=data.customer_last_name,
        customer_phone=data.customer_phone,
        customer_street_address=data.customer_street_address,
    )

    if new_job.who_pays == s.Job.WhoPays.ME:
        new_job.commission_status = s.enums.CommissionStatus.PAID

    db.add(new_job)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new job"
        )

    job_created_notify(new_job, db)
    log(log.INFO, "Job [%s] created successfully", new_job.id)

    return new_job


@job_router.patch("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def patch_job(
    job_data: s.JobPatch,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
):
    initial_job = s.Job.from_orm(job)
    try:
        if job_data.profession_id:
            job.profession_id = job_data.profession_id
        if job_data.city:
            job.city = job_data.city
        if job_data.payment:
            job.payment = job_data.payment
        if job_data.commission:
            job.commission = job_data.commission
        if job_data.name:
            job.name = job_data.name
        if job_data.description:
            job.description = job_data.description
        if job_data.time:
            job.time = job_data.time
        if job_data.customer_first_name:
            job.customer_first_name = job_data.customer_first_name
        if job_data.customer_last_name:
            job.customer_last_name = job_data.customer_last_name
        if job_data.customer_phone:
            job.customer_phone = job_data.customer_phone
        if job_data.customer_street_address:
            job.customer_street_address = job_data.customer_street_address
    except ValueDownGradeForbidden as e:
        log(log.ERROR, "Error while patching job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error patching job"
        )

    job.status = s.enums.JobStatus(job_data.status)
    job.payment_status = s.enums.PaymentStatus(job_data.payment_status)
    job.commission_status = s.enums.CommissionStatus(job_data.commission_status)

    if job_data.status:
        handle_job_status_update_notification(current_user, job, db, initial_job)

    if job_data.payment_status:
        handle_job_payment_notification(current_user, job, db, initial_job)

    if job_data.commission_status:
        handle_job_commission_notification(current_user, job, db, initial_job)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while patching job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error patching job"
        )

    log(log.INFO, "Job [%s] patched successfully", job.name)
    return job


@job_router.put("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def update_job(
    job_data: s.JobUpdate,
    current_user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
    db: Session = Depends(get_db),
):
    initial_job = s.Job.from_orm(job)
    try:
        job.profession_id = job_data.profession_id
        job.city = job_data.city
        job.payment = job_data.payment
        job.commission = job_data.commission
        job.name = job_data.name
        job.description = job_data.description
        job.time = job_data.time
        job.customer_first_name = job_data.customer_first_name
        job.customer_last_name = job_data.customer_last_name
        job.customer_phone = job_data.customer_phone
        job.customer_street_address = job_data.customer_street_address
        job.status = s.enums.JobStatus(job_data.status)
        job.payment_status = s.enums.PaymentStatus(job_data.payment_status)
        job.commission_status = s.enums.CommissionStatus(job_data.commission_status)
    except ValueDownGradeForbidden as e:
        log(log.ERROR, "Error while updating job [%i] - %s", job.id, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating job"
        )

    handle_job_status_update_notification(current_user, job, db, initial_job)
    handle_job_payment_notification(current_user, job, db, initial_job)
    handle_job_commission_notification(current_user, job, db, initial_job)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating job"
        )

    log(log.INFO, "Job [%s] updated successfully", job.name)
    return job


@job_router.delete("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def delete_job(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
):
    if current_user != job.owner:
        log(log.INFO, "User [%s] is not related to job", current_user.first_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User not related",
        )

    job.is_deleted = True
    devices_tokens = []
    for application in job.applications:
        notification: m.Notification = m.Notification(
            user_id=application.worker.id,
            entity_id=job.id,
            type=s.enums.NotificationType.JOB_CANCELED,
        )
        db.add(notification)
        if application.worker.notification_job_status:
            for device in application.worker.devices:
                devices_tokens.append(device.push_token)
    if devices_tokens:
        push_handler = PushHandler()
        push_handler.send_notification(
            s.PushNotificationMessage(
                device_tokens=devices_tokens,
                payload=get_notification_payload(
                    notification_type=notification.type, job=job
                ),
            )
        )

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while deleting job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error deleting job"
        )

    log(log.INFO, "Job [%s] deleted successfully", job.name)
    return job
