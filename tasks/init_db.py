import random
from sqlalchemy import select
from invoke import task
from app.config import Settings, get_settings
from app.model import User, Profession, Job
from app.logger import log
from tests.utility import create_locations as cl, create_professions, create_jobs as cj
from tests.utility.create_test_users import fill_test_data

settings: Settings = get_settings()


NUM_TEST_JOBS = 27
TEST_CITIES = [
    "Afula",
    "Akko",
    "Arad",
    "Ariel",
    "Ashdod",
    "Ashkelon",
    "Ashkelon",
    "Baqa al-Gharbiyye",
    "Bat Yam",
    "Beer Sheva",
    "Beit Shean",
    "Beit Shemesh",
    "Betar Illit",
    "Bnei Berak",
    "Dimona",
    "Eilat",
    "Elad",
    "Givatayim",
]

TEST_TIMES = [
    "Within next 3h",
    "ASAP",
]


@task
def create_locations(_):
    from app.database import db as dbo

    db = dbo.Session()
    cl(db)


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
    cj(db)
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
        payment = 25 + uid
        job = Job(
            owner_id=owners[uid].id,
            profession_id=professions[uid].id,
            name="name",
            description="description",
            payment=payment,
            commission=payment * 0.25,
            city=random.choice(TEST_CITIES),
            time=random.choice(TEST_TIMES),
        )
        db.add(job)
    db.commit()
    log(log.INFO, "Jobs [%d] created", NUM_TEST_JOBS)
