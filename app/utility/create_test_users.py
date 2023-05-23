from sqlalchemy.orm import Session
from app import model as m

NUM_TEST_USERS = 100


def fill_test_data(db: Session):
    for uid in range(NUM_TEST_USERS):
        user = m.User(
            username=f"User{uid}",
            first_name=f"Jack{uid}",
            last_name=f"London{uid}",
            password_hash=f"{uid}",
            email=f"user{uid}@test.com",
            phone=f"972 54 000 {uid+1:04}",
            is_verified=True,
        )
        db.add(user)
    db.commit()
