import random

from sqlalchemy.orm import Session
from app import model as m
from app import schema as s
from app.logger import log

NUM_TEST_USERS = 100
MAX_RATES_NUM = 5


def fill_test_data(db: Session):
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
        )
        db.add(user)

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

    log(log.INFO, "Users [%d] were created", NUM_TEST_USERS)
    log(log.INFO, "Rates [%d] were created", rates_num_total)
