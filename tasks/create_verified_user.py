from invoke import task

# from sqlalchemy.orm import Session
from app.model import User

TEST_USER_FIRST_NAME = "Mark"
TEST_USER_LAST_NAME = "Levy"
TEST_USER_PHONE = "000 000 0000 00"
TEST_PASSWORD = "password"


@task
def create_verified_user(_):
    """Create a verified user"""

    from app.database import db

    with db.begin() as conn:
        user: User = User(
            phone=TEST_USER_PHONE,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
            password_hash=TEST_PASSWORD,
            is_verified=True,
        )
        conn.add(user)
        conn.commit()
    print(f"{TEST_USER_FIRST_NAME} {TEST_USER_LAST_NAME} created")
