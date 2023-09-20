import random

from invoke import task
from sqlalchemy import select
from fastapi import status

from app.logger import log
from tests.utility import create_jobs as cj, create_jobs_for_user as cjfu


JOB_NAME = "-=test_job=-"
JOB_DESCRIPTION = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et do
lore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamc
o laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure d
olor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
"""

OWNER_PASSWORD = "pass"
OWNER_PHONE = "001"


@task
def create_jobs(_):
    from app.database import db as dbo

    db = dbo.Session()
    cj(db)


@task
def create_jobs_for_user(_, user_id: int):
    from app.database import db as dbo

    db = dbo.Session()
    cjfu(db, user_id)


@task
def create_job(
    ctx,
    name: str = JOB_NAME,
    description: str = JOB_DESCRIPTION,
    profession: str = "Handyman",
    city: str = "Ariel",
    owner_phone: str | None = OWNER_PHONE,
    owner_password: str | None = OWNER_PASSWORD,
):
    """creates job with given name, description, profession and city

    Args:
        name (str, optional): job name. Defaults to JOB_NAME.
        description (str, optional): job description. Defaults to JOB_DESCRIPTION.
        profession (str, optional): job profession. Defaults to "Handyman".
        city (str, optional): job city. Defaults to "Ariel".
        owner_phone (str, optional): owner phone. Defaults to OWNER_PHONE.
        owner_password (str, optional): owner password. Defaults to OWNER_PASSWORD.
    """

    from datetime import datetime

    from fastapi.testclient import TestClient

    from .user import login_user
    from app.database import db as dbo
    from app.main import app
    from app import schema as s
    from app import model as m
    from tests.utility import create_locations, create_professions

    db = dbo.Session()

    if db.scalar(select(m.Job).where(m.Job.name == name)):
        log(log.WARNING, "Job [%s] already exists", name)
        return db.scalar(select(m.Job).where(m.Job.name == name))

    token = login_user(ctx, owner_phone, owner_password)

    create_professions(db)
    create_locations(db)
    locations = [location.id for location in db.scalars(select(m.Location)).all()]

    with TestClient(app) as client:
        profession_id: int = db.scalar(
            select(m.Profession.id).where(m.Profession.name_en == profession)
        )
        assert profession_id
        job_data = s.JobIn(
            profession_id=profession_id,
            city=city,
            payment=1111,
            commission=10,
            who_pays=s.Job.WhoPays.ME,
            name=name,
            is_asap=True,
            description=description,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_first_name="Mykola",
            customer_last_name="Černov",
            customer_phone="+380123456789",
            customer_street_address="Kyiv",
            regions=[random.choice(locations)],
        )
        response = client.post(
            "/api/job",
            headers={"Authorization": f"Bearer {token}"},
            json=job_data.dict(),
        )

        if response.status_code != status.HTTP_201_CREATED:
            log(log.ERROR, "Job creating failed")
            return

        log(log.INFO, "Job created")

        return db.scalar(select(m.Job).where(m.Job.name == name))


@task
def create_job_for_notification(
    ctx,
    owner_phone: str | None = OWNER_PHONE,
    owner_password: str | None = OWNER_PASSWORD,
    name: str = JOB_NAME,
    description: str = JOB_DESCRIPTION,
    location_id: int | None = 1,
    profession_id: int | None = 1,
):
    """creates job with given name, description, profession and city for creating notification

    Args:
        owner_phone (str, optional): owner phone. Defaults to OWNER_PHONE.
        owner_password (str, optional): owner password. Defaults to OWNER_PASSWORD.
        name (str, optional): job name. Defaults to JOB_NAME.
        description (str, optional): job description. Defaults to JOB_DESCRIPTION.
        location_id (int, optional): job location id. Defaults to 1.
        profession_id (int, optional): job profession id. Defaults to 1.
    """

    from datetime import datetime

    from fastapi.testclient import TestClient

    from .user import login_user, create_user
    from app.database import db as dbo
    from app.main import app
    from app import schema as s
    from app import model as m

    db = dbo.Session()

    create_user(ctx, owner_phone, owner_password, location_id, profession_id)
    token: str = login_user(ctx, owner_phone, owner_password)
    user: m.User = db.scalar(select(m.User).where(m.User.phone == owner_phone))

    if not user:
        log(log.ERROR, "User [%s] not found", owner_phone)
        return

    if not (user.professions or user.locations):
        log(log.ERROR, "User [%s] has no professions and locations", owner_phone)
        return

    with TestClient(app) as client:
        profession_id: int = (
            db.scalar(select(m.Profession.id))
            if not user.professions
            else user.professions[0].id
        )

        city: m.Location = (
            db.scalar(select(m.Location)) if not user.locations else user.locations[0]
        )
        job_data = s.JobIn(
            profession_id=profession_id,
            city=city.name_en,
            payment=1111,
            commission=10,
            who_pays=s.Job.WhoPays.ME,
            name=name,
            description=description,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_first_name="Mykola",
            customer_last_name="Černov",
            customer_phone="+380123456789",
            customer_street_address="Kyiv",
        )
        response = client.post(
            "/api/job",
            headers={"Authorization": f"Bearer {token}"},
            json=job_data.dict(),
        )
        if response.status_code != status.HTTP_201_CREATED:
            log(log.ERROR, "Job creating failed")
            return

        log(log.INFO, "Job created")

        return db.scalar(select(m.Job).where(m.Job.name == name))


@task
def patch_job_status(
    ctx,
    name: str = JOB_NAME,
    owner_phone: str | None = OWNER_PHONE,
    owner_password: str | None = OWNER_PASSWORD,
):
    """updates job status to next stage

    Args:
        name (str, optional): job name. Defaults to "-=test_job=-".
        owner_phone (str | None): Defaults to "001".
        owner_password (str | None): Defaults to "string".
    """

    from fastapi.testclient import TestClient

    from .user import login_user
    from app.database import db as dbo
    from app.main import app
    from app import schema as s
    from app import model as m

    db = dbo.Session()

    token: str = login_user(ctx, owner_phone, owner_password)
    job = db.scalar(select(m.Job).where(m.Job.name == name))
    if not job:
        log(log.ERROR, "Job [%s] not found", name)
        return

    with TestClient(app) as client:
        try:
            next_job_status = job.status.next()
        except IndexError:
            log(log.ERROR, "Job status is already last")
            return

        job_data = s.JobPatch(
            status=next_job_status,
        )
        response = client.patch(
            f"api/job/{job.uuid}",
            headers={"Authorization": f"Bearer {token}"},
            json=job_data.dict(),
        )
        if response.status_code != status.HTTP_200_OK:
            log(log.ERROR, "Job status updating failed")
            return

        log(log.INFO, "Job status updated")

        return db.scalar(select(m.Job).where(m.Job.name == name))
