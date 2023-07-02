from invoke import task
from sqlalchemy import select, and_
from fastapi import status

from app.logger import log
from .job import create_job


WORKER_PHONE = "002"
WORKER_PASSWORD = "pass"


@task
def create_application(ctx, job_id: int | None = None):
    """create application for given job

    Args:
        job_id (int, optional): job id. Defaults to None (gets from create-job).
    """
    from fastapi.testclient import TestClient
    from .user import login_user
    from app.database import db as dbo
    from app.main import app

    from app import schema as s
    from app import model as m

    db = dbo.Session()

    if not job_id:
        job = create_job(ctx)
    else:
        job = db.scalar(
            select(m.Job).where(
                and_(m.Job.id == job_id, m.Job.status == s.enums.JobStatus.PENDING)
            )
        )

        if not job:
            log(log.ERROR, "Job [%s] not found", job_id)
            return

    token = login_user(ctx)

    with TestClient(app) as client:
        request_data: s.ApplicationIn = s.ApplicationIn(job_id=job.id)

        response = client.post(
            "api/application",
            headers={"Authorization": f"Bearer {token}"},
            json=request_data.dict(),
        )

        if response.status_code != status.HTTP_201_CREATED:
            log(log.ERROR, "Application creating failed")
            return

        log(log.INFO, "Application created")


@task
def create_application_for_notification(
    ctx,
    job_id: int | None = None,
    worker_phone: str | None = WORKER_PHONE,
    worker_password: str | None = WORKER_PASSWORD,
):
    """create application for given job

    Args:
        job_id (int, optional): job id. Defaults to None (gets from create-job).
        worker_phone (str, optional): worker phone. Defaults to "001".
        worker_password (str, optional): worker password. Defaults to "pass".
    """
    from fastapi.testclient import TestClient
    from .user import login_user, create_user
    from app.database import db as dbo
    from app.main import app

    from app import schema as s
    from app import model as m

    db = dbo.Session()

    create_user(ctx, worker_phone, worker_password)
    token = login_user(ctx, worker_phone, worker_password)

    if not job_id:
        job = create_job(ctx)
    else:
        job = db.scalar(
            select(m.Job).where(
                and_(m.Job.id == job_id, m.Job.status == s.enums.JobStatus.PENDING)
            )
        )

    with TestClient(app) as client:
        request_data: s.ApplicationIn = s.ApplicationIn(job_id=job.id)

        response = client.post(
            "api/application",
            headers={"Authorization": f"Bearer {token}"},
            json=request_data.dict(),
        )

        if response.status_code != status.HTTP_201_CREATED:
            log(log.ERROR, "Application creating failed")
            return

        log(log.INFO, "Application created")
