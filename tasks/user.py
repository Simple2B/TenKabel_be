from invoke import task
from sqlalchemy import select, and_
from fastapi import status


from app.model import (
    User,
    Profession,
    Application,
    Location,
    UserLocation,
    UserProfession,
    UserNotificationLocation,
    UserNotificationsProfessions,
    PlatformCommission,
)
from app.logger import log

TEST_USER_PHONE = "001"
TEST_PASSWORD = "pass"
TEST_EMAIL_END = "@test.com"


@task
def create_user(
    _,
    telephone: str = TEST_USER_PHONE,
    password: str = TEST_PASSWORD,
    location_id: int | None = None,
    profession_id: int | None = None,
):
    """create user with given telephone and password

    Args:
        telephone (str, optional): user phone. Default value is "001".
        password (str, optional): user password. Default value is "pass".
        location_id (int, optional): user location id. Default value is None.
        profession_id (int, optional): user profession id. Default value is None.
    """

    from app.database import db

    first_name = "FIRST" + telephone[-3:]
    last_name = "LAST" + telephone[-3:]
    email = first_name + TEST_EMAIL_END

    with db.begin() as conn:
        query = select(User).where(User.email == email)
        user = conn.scalar(query)
        if not user:
            user: User = User(
                phone=telephone,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_verified=True,
                country_code="LI",
                payplus_customer_uid="test_uid",
            )
            conn.add(user)
            profession: Profession | None = conn.scalar(
                select(Profession).where(Profession.id == profession_id)
            )

            if profession:
                conn.add(
                    UserProfession(
                        user_id=user.id,
                        profession_id=profession_id,
                    )
                )
                log(log.INFO, "User's profession created [%s]", profession.name_en)

            location: Location | None = conn.scalar(
                select(Location).where(Location.id == location_id)
            )

            if location:
                conn.add(
                    UserLocation(
                        user_id=user.id,
                        location_id=location_id,
                    )
                )
                log(log.INFO, "User's location created [%s]", location.name_en)

            conn.commit()
            log(
                log.INFO,
                "%s %s - %s created",
                first_name,
                last_name,
                email,
            )
        else:
            log(log.WARNING, "User %s already exists", email)


@task
def login_user(
    _,
    telephone: str = TEST_USER_PHONE,
    password: str = TEST_PASSWORD,
):
    """user login with given telephone and password

    Args:
        telephone (str, optional): user phone. Defaults to "001".
        password (str, optional): user password. Defaults to "pass".
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from app import schema as s

    with TestClient(app) as client:
        user_data = s.AuthUser(
            phone=telephone,
            password=password,
            country_code="LI",
        )

        response = client.post(
            "/api/auth/login-by-phone",
            json=user_data.dict(),
        )
        if response.status_code != status.HTTP_200_OK:
            log(log.ERROR, "User login failed")
            return

        token = s.Token.parse_obj(response.json())
        log(log.INFO, "User token: %s", token.access_token)
        return token.access_token


@task
def delete_user(_, phone: str = TEST_USER_PHONE, email: str | None = None):
    """delete user with given telephone or email

    Args:
        phone (str, optional): user phone. Defaults to "001".
        email (str, optional): user email. Defaults to None.
    """
    from app.database import db as dbo

    db = dbo.Session()
    if email:
        user = db.scalar(select(User).where(User.email == email))
    else:
        user = db.scalar(select(User).where(User.phone == phone))

    if not user:
        log(log.WARNING, "User not found")
        return

    for pp in user.platform_payments:
        db.delete(pp)
        log(log.INFO, "Platform payment deleted")

    for job in user.jobs_to_do:
        for application in job.applications:
            log(log.INFO, "Application deleted [%s]", application.job.name)
            db.delete(application)
            db.commit()
        pps = db.scalars(
            select(PlatformCommission).where(PlatformCommission.job_id == job.id)
        ).all()
        for pp in pps:
            db.delete(pp)
            log(log.INFO, "Platform commission deleted")
        for rate in job.rates:
            db.delete(rate)
            log(log.INFO, "Rate deleted")
        log(log.INFO, "Job deleted [%s]", job.name)
        db.delete(job)

    for job in user.jobs_owned:
        for application in job.applications:
            log(log.INFO, "Application deleted [%s]", application.job.name)
            db.delete(application)
            db.commit()

        pps = db.scalars(
            select(PlatformCommission).where(PlatformCommission.job_id == job.id)
        ).all()
        for pp in pps:
            db.delete(pp)
            log(log.INFO, "Platform commission deleted")
        for rate in job.rates:
            db.delete(rate)
            log(log.INFO, "Rate deleted")

        log(log.INFO, "Job deleted [%s]", job.name)
        db.delete(job)

    for profession in user.professions:
        log(log.INFO, "User profession deleted [%s]", profession.name_en)

        db.delete(
            db.scalar(
                select(UserProfession).where(
                    and_(
                        UserProfession.profession_id == profession.id,
                        UserProfession.user_id == user.id,
                    )
                )
            )
        )
        db.flush()

    for location in user.locations:
        log(log.INFO, "User location deleted [%s]", location.name_en)
        db.delete(
            db.scalar(
                select(UserLocation).where(
                    and_(
                        UserLocation.location_id == location.id,
                        UserLocation.user_id == user.id,
                    )
                )
            )
        )
        db.flush()

    for location in user.notification_locations:
        log(log.INFO, "User location deleted [%s]", location.name_en)
        db.delete(
            db.scalar(
                select(UserNotificationLocation).where(
                    and_(
                        UserNotificationLocation.location_id == location.id,
                        UserNotificationLocation.user_id == user.id,
                    )
                )
            )
        )
        db.flush()

    for profession in user.notification_profession:
        log(log.INFO, "User profession deleted [%s]", profession.name_en)

        db.delete(
            db.scalar(
                select(UserNotificationsProfessions).where(
                    and_(
                        UserNotificationsProfessions.profession_id == profession.id,
                        UserNotificationsProfessions.user_id == user.id,
                    )
                )
            )
        )
        db.flush()

    for device in user.devices:
        log(log.INFO, "User device deleted [%s]", device.push_token)
        db.delete(device)
        db.flush()

    applications = db.scalars(
        select(Application).where(Application.worker_id == user.id)
    ).all()
    applications += db.scalars(
        select(Application).where(Application.owner_id == user.id)
    ).all()

    for application in applications:
        log(log.INFO, "Application deleted [%s]", application.job.name)
        db.delete(application)
        db.flush()

    for notification in user.notifications:
        log(log.INFO, "Notification deleted [%s]", notification.type)
        db.delete(notification)
        db.flush()

    db.commit()
    log(log.INFO, "User %s deleted", phone)
    db.delete(user)
    db.commit()
