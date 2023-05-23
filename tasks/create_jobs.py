from invoke import task

from app.utility import create_jobs as cj


@task
def create_jobs(_):
    """Create a verified user for test"""
    from app.database import db as dbo

    db = dbo.Session()
    cj(db)
