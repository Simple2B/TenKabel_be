import random
from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.model as m
import app.schema as s
from app.utility import (
    fill_test_data,
    create_locations,
    create_professions,
    create_jobs,
)

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
TEST_MIN_PRICE = 1
TEST_MAX_PRICE = 40


def test_jobs(client: TestClient, db: Session):
    # create users
    fill_test_data(db)
    # create professions
    create_professions(db)
    # get all users
    owners = db.query(m.User).all()
    # get locations
    create_locations(db)
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
    response = client.get("api/job/jobs")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    assert len(resp_obj.jobs) > 0

    # filtering jobs with profession_id=1
    response = client.get("api/job/jobs?profession_id=1")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.profession_id == 1

    # filtering jobs with profession_id=1
    test_location = db.query(m.Location).first()
    assert test_location
    response = client.get(f"api/job/jobs?city={test_location.name_en}")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.city == test_location.name_en

    response = client.get(f"api/job/jobs?city=  ){test_location.name_en} & && !*?'  ")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.city == test_location.name_en

    # filtering jobs by min price
    response = client.get(f"api/job/jobs?min_price={TEST_MIN_PRICE}")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.payment >= TEST_MIN_PRICE

    # filtering jobs by max price
    response = client.get(f"api/job/jobs?max_price={TEST_MAX_PRICE}")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.payment <= TEST_MAX_PRICE

    # get single job
    job: m.Job = db.query(m.Job).first()
    assert job
    response = client.get(f"api/job/{job.uuid}/")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Job.parse_obj(response.json())
    assert resp_obj.uuid == job.uuid


def test_create_job(
    client: TestClient,
    db: Session,
    authorized_users_tokens: list[s.Token],
):
    request_data = s.JobIn(
        profession_id=1,
        city="Test City",
        payment=10000,
        commission=10000,
        name="Test Task",
        description="Just do anything",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ).dict()
    response = client.post(
        "api/job",
        json=request_data,
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert db.query(m.Job).filter_by(city=request_data["city"]).first()


def test_search_job(
    client: TestClient,
    db: Session,
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    response = client.get("api/job/search")
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    job: m.Job = db.scalar(select(m.Job))
    assert job

    response = client.get("api/job/search", params={"city": f"{job.city}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0
    assert all([resp_job.city == job.city for resp_job in response_jobs_list.jobs])

    response = client.get("api/job/search", params={"title": f"{job.name}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    response = client.get("api/job/search", params={"title": f"{job.description}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    response = client.get(
        "api/job/search", params={"city": "non_existin_city_for_sure_123"}
    )
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) == 0
