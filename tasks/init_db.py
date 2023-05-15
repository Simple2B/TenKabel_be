from sqlalchemy import select
from invoke import task
from app.config import Settings, get_settings
from app.model import User, Profession, Job
from app.logger import log
from app.utility import create_locations, create_professions
from app.utility.create_test_users import fill_test_data

settings: Settings = get_settings()


NUM_TEST_JOBS = 27


@task
def init_db(_, test_data=False):
    """Initialization database

    Args:
        --test-data (bool, optional): wether fill database by test data. Defaults to False.
    """
    from app.database import db as dbo

    db = dbo.Session()
    create_professions(db)
    create_locations(db)
    # add admin user
    admin = User(
        username=settings.ADMIN_USER,
        password=settings.ADMIN_PASS,
        email=settings.ADMIN_EMAIL,
        phone="972 54 000 00000",
        is_verified=True,
    )
    db.add(admin)
    if test_data:
        # Add test data
        fill_test_data(db)

    db.commit()


@task
def create_jobs(_):
    """Create test jobs"""
    from app.database import db as dbo

    db = dbo.Session()
    owners = db.scalars(select(User).order_by(User.id)).all()
    log(log.INFO, "Owners [%d] ", len(owners))
    professions = db.scalars(select(Profession).order_by(Profession.id)).all()
    log(log.INFO, "Professions [%d] ", len(professions))
    for uid in range(NUM_TEST_JOBS):
        job = Job(
            owner_id=owners[uid].id,
            profession_id=professions[uid].id,
            name="name",
            description="description",
        )
        db.add(job)
    db.commit()
    log(log.INFO, "Jobs [%d] created", NUM_TEST_JOBS)
