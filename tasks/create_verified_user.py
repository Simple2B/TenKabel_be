from invoke import task
from sqlalchemy import select

# from sqlalchemy.orm import Session
from app.model import User

TEST_USER_FIRST_NAME = "Mark"
TEST_USER_LAST_NAME = "Levy"
TEST_USER_PHONE = "+972 55 555 0000"
TEST_PASSWORD = "pass"
TEST_USER_EMAIL = "test@example.com"


@task
def create_verified_user(_):
    """Create a verified user for test"""

    from app.database import db
    from app.logger import log

    with db.begin() as conn:
        user = db.scalar(select(User).where(User.email == TEST_USER_EMAIL))
        if not user:
            user: User = User(
                phone=TEST_USER_PHONE,
                email=TEST_USER_EMAIL,
                first_name=TEST_USER_FIRST_NAME,
                last_name=TEST_USER_LAST_NAME,
                password=TEST_PASSWORD,
                is_verified=True,
            )
            conn.add(user)
            conn.commit()
            log(
                log.INFO,
                "%s %s - %s created",
                TEST_USER_FIRST_NAME,
                TEST_USER_LAST_NAME,
                TEST_USER_EMAIL,
            )
        else:
            log(log.INFO, "User %s already exists", TEST_USER_EMAIL)
