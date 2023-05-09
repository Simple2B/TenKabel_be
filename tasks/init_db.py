from sqlalchemy.orm import Session
from invoke import task
from app.config import Settings, get_settings
from app.model import User

settings: Settings = get_settings()

NUM_TEST_USERS = 1000


@task
def init_db(_, test_data=False):
    """Initialization database

    Args:
        --test-data (bool, optional): wether fill database by test data. Defaults to False.
    """
    from app.database import db as dbo

    db = dbo.Session()
    # add admin user
    admin = User(
        username=settings.ADMIN_USER,
        password=settings.ADMIN_PASS,
        email=settings.ADMIN_EMAIL,
        phone="972 54 000 00000",
    )
    db.add(admin)
    if test_data:
        # Add test data
        fill_test_data(db)

    db.commit()


def fill_test_data(db: Session):
    for uid in range(NUM_TEST_USERS):
        user = User(
            username=f"User{uid}",
            first_name=f"Jack{uid}",
            last_name=f"London{uid}",
            email=f"user{uid}@test.com",
            phone=f"972 54 000 {uid+1:04}",
        )
        db.add(user)
