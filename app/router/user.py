import datetime

from fastapi import HTTPException, Depends, APIRouter, status, Form
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import app.model as m
import app.schema as s
from app.logger import log
from app.dependency import get_current_user
from app.database import get_db
from app.hash_utils import hash_verify


user_router = APIRouter(prefix="/user", tags=["Users"])


@user_router.get("", response_model=s.User)
def get_current_user_profile(
    current_user: m.User = Depends(get_current_user),
):
    return current_user


@user_router.put("", status_code=status.HTTP_200_OK)
def update_user(
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
        current_user.picture = picture
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
    return status.HTTP_200_OK


@user_router.post("/check-password", status_code=status.HTTP_200_OK)
def check_password(
    password: str,
    current_user: m.User = Depends(get_current_user),
):
    if not hash_verify(password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Password does not match"
        )
    return status.HTTP_200_OK


@user_router.post("/forgot-password", status_code=status.HTTP_201_CREATED)
def forgot_password(
    data: s.ForgotPassword,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(m.User).where(m.User.phone == data.phone))
    user.password = data.new_password
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(log.INFO, "Error while updating user password - %s", e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Error updating password"
        )

    log(log.INFO, "User [%s] password updated successfully", user.username)
    return status.HTTP_201_CREATED


@user_router.post("/change-password", status_code=status.HTTP_201_CREATED)
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
    return status.HTTP_201_CREATED


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
            m.Application.owner_id == current_user.id
            and m.Application.status == s.BaseApplication.ApplicationStatus.PENDING
        )
    elif type == "worker":
        query = query.where(m.Application.worker_id == current_user.id).filter(
            m.Application.created_at
            > datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
        )
    else:
        log(log.INFO, "Wrong filter %s", type)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wrong filter")

    log(log.INFO, "[%s] type applications for User [%s]", type, current_user.username)
    return s.ApplicationList(applications=db.scalars(query).all())


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
                "Pending tab, getting jobs ids for user: (%s)",
                str(current_user.id),
            )
            jobs_ids = db.scalars(
                select(m.Application.job_id).where(
                    or_(
                        m.Application.worker_id == current_user.id,
                        m.Application.owner_id == current_user.id,
                    )
                )
            ).all()
            query = query.filter(m.Job.id.in_(jobs_ids))
            log(log.INFO, "Jobs filtered by ids: (%s)", ",".join(map(str, jobs_ids)))

        if manage_tab == s.Job.TabFilter.ACTIVE:
            query = query.where(
                or_(
                    m.Job.status == s.Job.Status.IN_PROGRESS,
                    m.Job.status == s.Job.Status.APPROVED,
                )
            )
            log(log.INFO, "Jobs filtered by status: %s", manage_tab)
        if manage_tab == s.Job.TabFilter.ARCHIVE:
            # TODO: add cancel field search in jobs
            query = query.filter(m.Job.status == s.Job.Status.JOB_IS_FINISHED)
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
