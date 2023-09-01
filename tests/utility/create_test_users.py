import random
import base64

from sqlalchemy import select

from sqlalchemy.orm import Session
from app import model as m
from app.logger import log
from app.utility import generate_uuid

NUM_TEST_USERS = 100
TEST_IMAGES = []


for num in range(1, 6):
    with open(f"tests/utility/images/test_avatar_{num}.png", "rb") as f:
        byte_data = f.read()
        picture = base64.b64encode(byte_data).decode("utf-8")
        TEST_IMAGES.append(picture)


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
            email=f"user{uid_user}_{generate_uuid()}@test.com",
            phone=f"972 54 000 {uid_user+1:04}",
            country_code="IL",
            is_verified=True,
            picture=random.choice(TEST_IMAGES),
        )
        db.add(user)

    log(log.INFO, "Users [%d] were created", NUM_TEST_USERS)
    db.flush()

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
