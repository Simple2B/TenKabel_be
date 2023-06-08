import random
from sqlalchemy import select

from sqlalchemy.orm import Session
from app import model as m
from app import schema as s
from app.logger import log

NUM_TEST_USERS = 100
MAX_RATES_NUM = 5
TEST_IMAGES = []


TEST_AVATAR_URLS = [
    "https://storage.googleapis.com/tenkabel/images/avatars/test_images/test_avatar_1.png",
    "https://storage.googleapis.com/tenkabel/images/avatars/test_images/test_avatar_2.png",
    "https://storage.googleapis.com/tenkabel/images/avatars/test_images/test_avatar_3.png",
    "https://storage.googleapis.com/tenkabel/images/avatars/test_images/test_avatar_5.png",
    "https://storage.googleapis.com/tenkabel/images/avatars/test_images/test_avatar_6.png",
]


def fill_test_data(db: Session):
    profession_ids = [profession.id for profession in db.scalars(select(m.Profession))]
    location_ids = [location.id for location in db.scalars(select(m.Location))]
    rates_num_total = 0
    for uid_user in range(NUM_TEST_USERS):
        user = m.User(
            username=f"User{uid_user}",
            first_name=f"Jack{uid_user}",
            last_name=f"London{uid_user}",
            password_hash=f"{uid_user}",
            email=f"user{uid_user}@test.com",
            phone=f"972 54 000 {uid_user+1:04}",
            is_verified=True,
            picture=random.choice(TEST_AVATAR_URLS),
        )
        db.add(user)

    log(log.INFO, "Users [%d] were created", NUM_TEST_USERS)

    db.commit()
    for uid_user in range(1, NUM_TEST_USERS):
        count_rates = random.randint(0, MAX_RATES_NUM)
        rates_num_total += count_rates
        for _ in range(count_rates):
            rate = m.Rate(
                worker_id=uid_user,
                owner_id=random.randint(1, NUM_TEST_USERS),
                rate=random.choice([e for e in s.BaseRate.RateStatus]),
            )
            db.add(rate)
    users: list[m.User] = db.scalars(select(m.User)).all()
    for user in users:
        if profession_ids:
            profession = db.scalar(
                select(m.Profession).where(
                    m.Profession.id == random.randint(1, len(profession_ids))
                )
            )
            db.add(
                m.UserProfession(
                    user_id=user.id,
                    profession_id=profession.id,
                )
            )
        if location_ids:
            location = db.scalar(
                select(m.Location).where(
                    m.Location.id == random.randint(1, len(location_ids))
                )
            )
            db.add(
                m.UserLocation(
                    user_id=user.id,
                    location_id=location.id,
                )
            )
            location = db.scalar(select(m.Location).where(m.Location.id != location.id))
            db.add(
                m.UserLocation(
                    user_id=user.id,
                    location_id=location.id,
                )
            )
        db.commit()
    log(log.INFO, "Rates [%d] were created", rates_num_total)
