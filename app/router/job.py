import re

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependency import get_current_user, get_user, get_job_by_uuid
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.utility import time_measurement
from app.utility.get_pending_jobs_query import get_pending_jobs_query_for_user
from app.controller import PushHandler
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
) -> s.ListJob:
    query = get_pending_jobs_query_for_user(db, user)

    if (
        user is None
        or user.google_openid_key
        or any([profession_id, city, min_price, max_price])
    ):
        if profession_id:
            query = query.where(m.Job.profession_id == profession_id)
        if city:
            city = re.sub(r"[^a-zA-Z0-9]", "", city)
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


@job_router.get("/search", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def search_job(
    q: str | None = "",
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_user),
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

    elif user:
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

    jobs: list[m.Job] = db.scalars(query.order_by(m.Job.created_at.desc())).all()
    log(log.INFO, "Job (%s) filtered by [%s] containing", len(jobs), q)
    return s.ListJob(jobs=jobs)


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
    current_user: m.User = Depends(get_current_user),
):
    new_job = m.Job(
        owner_id=current_user.id,
        profession_id=data.profession_id,
        name=data.name,
        description=data.description,
        payment=data.payment,
        commission=data.commission,
        city=data.city,
        time=data.time,
        customer_first_name=data.customer_first_name,
        customer_last_name=data.customer_last_name,
        customer_phone=data.customer_phone,
        customer_street_address=data.customer_street_address,
    )
    db.add(new_job)

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.ERROR, "Error while creating new job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error creating new job"
        )
    db.refresh(new_job)
    city: m.Location = db.scalar(
        select(m.Location).where(m.Location.name_en == new_job.city)
    )
    profession: m.Profession = db.scalar(
        select(m.Profession).where(m.Profession.id == new_job.profession_id)
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
            entity_id=new_job.id,
            type=s.NotificationType.JOB_CREATED,
        )
        db.add(notification)
        if (
            city in user.notification_locations and user.notification_locations_flag
        ) or (
            profession in user.notification_profession
            and user.notification_profession_flag
        ):
            for device in user.devices:
                devices.append(device.push_token)

    db.commit()

    push_handler = PushHandler()
    push_handler.send_notification(
        s.PushNotificationMessage(
            device_tokens=devices,
            payload=get_notification_payload(
                notification_type=s.NotificationType.JOB_CREATED, job=new_job
            ),
        )
    )

    log(log.INFO, "Job [%s] created successfully", new_job.id)
    log(log.INFO, "[%d] notifications created", len(users))
    return new_job


@job_router.patch("/{job_uuid}", status_code=status.HTTP_200_OK, response_model=s.Job)
def patch_job(
    job_data: s.JobPatch,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    job: m.Job = Depends(get_job_by_uuid),
):
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

    user = job.worker if current_user == job.owner else job.owner
    job.status = s.enums.JobStatus(job_data.status)
    job.payment_status = s.enums.PaymentStatus(job_data.payment_status)
    job.commission_status = s.enums.CommissionStatus(job_data.commission_status)

    if job_data.status and user:
        if job.status == s.enums.JobStatus.APPROVED:
            notification_type = s.NotificationType.JOB_STARTED
            db.add(
                m.PlatformPayment(
                    user_id=current_user.id,
                    job_id=job.id,
                    status=s.enums.PlatformPaymentStatus.PENDING,
                )
            )
            db.commit()

        if job.status == s.enums.JobStatus.JOB_IS_FINISHED:
            notification_type = s.NotificationType.JOB_DONE

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
                        notification_type=notification_type, job=job
                    ),
                )
            )

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while patching job - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error pathcing job"
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

    notification_type = None
    if job.status == s.enums.JobStatus.APPROVED:
        notification_type = s.NotificationType.JOB_STARTED

    if job.status == s.enums.JobStatus.JOB_IS_FINISHED:
        notification_type = s.NotificationType.JOB_DONE

    user = job.worker if current_user == job.owner else job.owner

    if notification_type and user:
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
