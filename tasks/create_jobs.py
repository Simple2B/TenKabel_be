from invoke import task

from tests.utility import create_jobs as cj, create_jobs_for_user as cjfu


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
