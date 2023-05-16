import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.utility import create_professions
import app.model as m

from app.utility.create_test_users import fill_test_data

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


def test_get_jobs(client: TestClient, db: Session):
    # create users
    fill_test_data(db)
    # create professions
    create_professions(db)
    # get all users
    owners = db.query(m.User).all()
    # get all professions
    professions = db.query(m.Profession).all()
    for uid in range(NUM_TEST_JOBS):
        payment = 25 + uid
        job = m.Job(
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
    response = client.get("api/jobs")
    assert response
