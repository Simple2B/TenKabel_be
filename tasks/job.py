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
):
    from datetime import datetime

    from fastapi.testclient import TestClient

    from .user import login_user
    from app.database import db as dbo
    from app.main import app
    from app import schema as s
    from app import model as m

    token = login_user(ctx)
    db = dbo.Session()

    with TestClient(app) as client:
        profession_id: int = db.scalar(
            select(m.Profession.id).where(m.Profession.name == profession)
        )
        assert profession_id
        job_data = s.JobIn(
            profession_id=profession_id,
            city=city,
            payment=1111,
            commission=10,
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
