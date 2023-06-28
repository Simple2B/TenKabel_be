from invoke import task
from sqlalchemy import select
from fastapi import status

from app.logger import log
from tests.utility import create_jobs as cj, create_jobs_for_user as cjfu
from .job import create_job, JOB_NAME


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
        job = db.scalar(select(m.Job).where(m.Job.id == job_id))

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
