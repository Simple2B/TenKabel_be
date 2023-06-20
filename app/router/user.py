import datetime

from fastapi import HTTPException, Depends, APIRouter, status, Form
from sqlalchemy import select, or_, and_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user
from app.database import get_db
from app.hash_utils import hash_verify


user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", status_code=status.HTTP_200_OK, response_model=s.User)
def get_current_user_profile(
    current_user: m.User = Depends(get_current_user),
):
    return current_user


@user_router.patch("", status_code=status.HTTP_200_OK, response_model=s.User)
def patch_user(
    data: s.UserUpdate,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    if data.first_name:
        current_user.username = data.username
        log(
            log.INFO,
            "User [%s] username updated - [%s]",
            current_user.id,
            data.username,
        )

    if data.first_name:
        current_user.first_name = data.first_name
        log(
            log.INFO,
            "User [%s] first_name updated - [%s]",
            current_user.id,
            data.first_name,
        )

    if data.last_name:
        current_user.last_name = data.last_name
        log(
            log.INFO,
            "User [%s] last_name updated - [%s]",
            current_user.id,
            data.last_name,
        )

    if data.email:
        current_user.email = data.email
        log(log.INFO, "User [%s] email updated - [%s]", current_user.id, data.email)
    if data.picture:
        current_user.picture = data.picture
        log(log.INFO, "User [%s] picture updated - [%s]", current_user.id, data.picture)
    if data.phone:
        current_user.phone = data.phone
        current_user.country_code = data.country_code
        log(log.INFO, "User [%s] phone updated - [%s]", current_user.id, data.phone)

    if data.professions:
        for profession in current_user.professions:
            profession_obj: m.UserProfession = db.scalar(
                select(m.UserProfession).where(
                    m.UserProfession.user_id == current_user.id,
                    m.UserProfession.profession_id == profession.id,
                )
            )
            db.delete(profession_obj)
        db.flush()
        for profession_id in data.professions:
            user_profession: m.UserProfession = db.scalar(
                select(m.UserProfession).where(
                    m.UserProfession.user_id == current_user.id,
                    m.UserProfession.profession_id == profession_id,
                )
            )
            if not user_profession:
                db.add(
                    m.UserProfession(
                        user_id=current_user.id, profession_id=profession_id
                    )
                )
                db.flush()

    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user [%s] - %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating user"
        )

    log(log.INFO, "User [%s] updated successfully", current_user.id)
    return current_user


@user_router.put("", status_code=status.HTTP_200_OK, response_model=s.User)
def update_user(
    # TODO: this method is unused
    email: str = Form(None),
    username: str = Form(None),
    phone: str = Form(None),
    first_name: str = Form(None),
    last_name: str = Form(None),
    professions: list[int] = Form(None),
    picture: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    if email:
        current_user.email = email
    if username:
        current_user.username = username
    if phone:
        current_user.phone = phone
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if picture:
        current_user.picture = bytes(picture, "UTF-8")
        log(log.INFO, "User [%s] picture update in progress...", current_user.username)
    if professions:
        for profession in current_user.professions:
            db.delete(profession)
            db.flush()
        for profession_id in professions:
            profession = db.scalar(
                select(m.Profession).where(m.Profession.id == profession_id)
            )
            user_profession = db.scalar(
                select(m.UserProfession).where(
                    m.UserProfession.user_id == current_user.id,
                    m.UserProfession.profession_id == profession_id,
                )
            )
            if not user_profession:
                db.add(
                    m.UserProfession(
                        user_id=current_user.id, profession_id=profession_id
                    )
                )
                db.flush()
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating user"
        )

    log(log.INFO, "User [%s] updated successfully", current_user.username)
    return current_user


@user_router.post(
    "/check-password", status_code=status.HTTP_200_OK, response_model=s.PasswordStatus
)
def check_password(
    password: str,
    current_user: m.User = Depends(get_current_user),
):
    if not hash_verify(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Password does not match"
        )
    return s.PasswordStatus(status=s.PasswordStatus.PasswordStatusEnum.PASSWORD_MATCH)


@user_router.post(
    "/forgot-password", status_code=status.HTTP_201_CREATED, response_model=s.User
)
def forgot_password(
    data: s.ForgotPassword,
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(m.User).where(
            and_(m.User.phone == data.phone, m.User.country_code == data.country_code)
        )
    )
    if not user:
        log(log.INFO, "User doesn't exist - %s %s", data.country_code, data.phone)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User does not exist"
        )

    user.password = data.new_password
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user password - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating password"
        )

    log(log.INFO, "User [%s] password updated successfully", user.username)
    return user


@user_router.post(
    "/change-password",
    status_code=status.HTTP_201_CREATED,
    response_model=s.PasswordStatus,
)
def change_password(
    data: s.ChangePassword,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    if not hash_verify(data.current_password, current_user.password):
        log(
            log.INFO, "Current password is not correct for user %s" % current_user.email
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bad current password"
        )

    current_user.password = data.new_password
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user password - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating password"
        )

    log(log.INFO, "User [%s] password updated successfully", current_user.username)
    return s.PasswordStatus(status=s.PasswordStatus.PasswordStatusEnum.PASSWORD_UPDATED)


@user_router.get(
    "/applications", status_code=status.HTTP_200_OK, response_model=s.ApplicationList
)
def get_user_applications(
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    query = select(m.Application)
    if not type:
        query = query.filter(
            or_(
                m.Application.worker_id == current_user.id,
                m.Application.owner_id == current_user.id,
            )
        )
    elif type == "owner":
        query = query.where(
            and_(
                m.Application.owner_id == current_user.id,
                m.Application.status == s.BaseApplication.ApplicationStatus.PENDING,
            )
        )
    elif type == "worker":
        query = query.where(m.Application.worker_id == current_user.id).filter(
            and_(
                m.Application.created_at
                > datetime.datetime.utcnow() - datetime.timedelta(weeks=1),
                m.Application.status == s.BaseApplication.ApplicationStatus.PENDING,
            )
        )
    else:
        log(log.INFO, "Wrong filter %s", type)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wrong filter")

    log(log.INFO, "[%s] type applications for User [%s]", type, current_user.username)
    applications = db.scalars(query.order_by(desc(m.Application.created_at))).all()
    applications_schema_list = [
        s.ApplicationOut.from_orm(application) for application in applications
    ]

    return s.ApplicationList(applications=applications_schema_list)


@user_router.get("/jobs", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_user_jobs(
    manage_tab: s.Job.TabFilter | None = None,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    query = select(m.Job).where(
        or_(m.Job.worker_id == current_user.id, m.Job.owner_id == current_user.id)
    )
    log(log.INFO, "Manage tab query parameter: (%s)", str(manage_tab))

    if manage_tab:
        try:
            manage_tab: s.Job.TabFilter = s.Job.TabFilter(manage_tab)
            log(log.INFO, "s.Job.TabFilter parameter: (%s)", manage_tab.value)
        except ValueError:
            log(log.INFO, "Filter manage tab doesn't exist - %s", manage_tab)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Wrong filter"
            )
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
                )
            )

            log(log.INFO, "Jobs filtered by ids: (%s)", ",".join(map(str, jobs_ids)))

        if manage_tab == s.Job.TabFilter.ACTIVE:
            query = query.where(
                m.Job.status == s.enums.JobStatus.IN_PROGRESS,
            )
            log(log.INFO, "Jobs filtered by status: %s", manage_tab)
        if manage_tab == s.Job.TabFilter.ARCHIVE:
            # TODO: add cancel field search in jobs
            query = query.filter(m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED)
            log(log.INFO, "Jobs filtered by status: %s", manage_tab)

    jobs: list[m.Job] = db.scalars(query.order_by(m.Job.created_at)).all()
    log(
        log.INFO,
        "User [%s] with id (%s) got [%s] jobs total",
        current_user.username,
        current_user.id,
        len(jobs),
    )
    return s.ListJob(jobs=jobs)


@user_router.get("/rates", status_code=status.HTTP_200_OK, response_model=s.RateList)
def get_user_rates(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    rates: s.RateList = db.scalars(
        select(m.Rate).where(m.Rate.worker_id == current_user.id)
    ).all()
    log(
        log.INFO,
        "User [%s] with id (%s) have [%s] rates total",
        current_user.username,
        current_user.id,
        len(rates),
    )
    return s.RateList(rates=rates)


@user_router.get("/postings", status_code=status.HTTP_200_OK, response_model=s.ListJob)
def get_user_postings(
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
):
    """Get list of jobs where current user is a owner"""
    query = select(m.Job).where(m.Job.owner_id == current_user.id)

    jobs: list[m.Job] = db.scalars(query.order_by(m.Job.created_at)).all()
    log(
        log.INFO,
        "User [%s] with id (%s) have [%s] jobs owning",
        current_user.username,
        current_user.id,
        len(jobs),
    )
    return s.ListJob(jobs=jobs)


@user_router.get("/{user_uuid}", response_model=s.User)
def get_user_profile(
    user_uuid: str,
    db: Session = Depends(get_db),
):
    user: m.User = db.scalars(select(m.User).where(m.User.uuid == user_uuid)).first()
    if not user:
        log(
            log.ERROR,
            "User %s not found",
            user_uuid,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    log(log.INFO, "User [%s] info", user.username)
    return user
