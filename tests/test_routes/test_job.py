from datetime import datetime

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

import app.model as m
import app.schema as s
from app.oauth2 import create_access_token
from tests.fixture import TestData
from tests.utility import (
    create_jobs,
    fill_test_data,
    create_locations,
    create_professions,
    create_jobs_for_user,
)


NUM_TEST_JOBS = 200
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


def test_auth_user_jobs(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    create_jobs(db, 300)

    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_authorized_users[0].phone)
    )
    assert user
    create_jobs_for_user(db, user.id)

    # check jobs are created
    response = client.get(
        "api/job/jobs",
        headers={
            "Authorization": f"Bearer {authorized_users_tokens[0].access_token}",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.ListJob = s.ListJob.parse_obj(response.json())
    for job in resp_obj.jobs:
        assert job.profession_id in [profession.id for profession in user.professions]
        assert job.city in [location.name_en for location in user.locations]
        assert job.owner_id != user.id


def test_unauth_user_jobs(client: TestClient, db: Session):
    # create users
    # create professions
    create_professions(db)
    # get locations
    create_locations(db)
    # create jobs
    create_jobs(db, NUM_TEST_JOBS)
    fill_test_data(db)

    # check jobs are created
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

    # regex checking
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
    user: m.User = db.scalar(select(m.User).where(m.User.id == resp_obj.owner_id))
    assert user.jobs_posted_count

    response = client.get("api/job/status_list")
    assert response.status_code == 200 and response.content


def test_create_job(
    client: TestClient,
    db: Session,
    authorized_users_tokens: list[s.Token],
):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)

    profession_id = db.scalar(select(m.Profession.id))
    city = db.scalar(select(m.Location))
    user = m.User(
        username="UserTestJobsCreate",
        first_name="Jack",
        last_name="JobTest",
        password_hash="123",
        email="usertest@test.com",
        phone="0663579795",
        country_code="IL",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    user_profession = m.UserProfession(user_id=user.id, profession_id=profession_id)
    user_location = m.UserLocation(user_id=user.id, location_id=city.id)
    db.add(user_location)
    db.add(user_profession)
    db.commit()

    request_data: s.JobIn = s.JobIn(
        profession_id=profession_id,
        city=city.name_en,
        payment=10000,
        commission=10000,
        name="Test Task",
        description="Just do anything",
        time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        customer_first_name="test_first_name",
        customer_last_name="test_last_name",
        customer_phone="+3800000000",
        customer_street_address="test_location",
    )
    response = client.post(
        "api/job",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert db.scalar(select(m.Job).filter_by(city=request_data.city))
    assert db.scalar(
        select(m.Job).filter_by(customer_last_name=request_data.customer_last_name)
    )
    assert db.scalar(select(m.Job).filter_by(name=request_data.name))
    assert db.scalar(
        select(m.Notification).where(
            and_(
                m.Notification.user_id == user.id,
                m.Notification.type == s.NotificationType.JOB_CREATED,
            )
        )
    )


def test_search_job(
    client: TestClient,
    db: Session,
):
    create_professions(db)
    create_jobs(db)
    fill_test_data(db)

    response = client.get("api/job/search")
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    for job in response_jobs_list.jobs:
        assert not job.is_deleted

    job: m.Job = db.scalar(
        select(m.Job).where(m.Job.status == s.enums.JobStatus.PENDING)
    )
    assert job

    response = client.get("api/job/search", params={"q": f"{job.city}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0
    assert all([resp_job.city == job.city for resp_job in response_jobs_list.jobs])

    response = client.get("api/job/search", params={"q": f"{job.name}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    response = client.get("api/job/search", params={"q": f"{job.description}"})
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) > 0

    response = client.get(
        "api/job/search", params={"q": "non_existin_city_for_sure_123"}
    )
    assert response.status_code == status.HTTP_200_OK
    response_jobs_list = s.ListJob.parse_obj(response.json())
    assert len(response_jobs_list.jobs) == 0


def test_update_job(
    client: TestClient,
    db: Session,
):
    create_professions(db)
    create_jobs(db)
    fill_test_data(db)

    job: m.Job = db.scalar(select(m.Job))
    user = job.owner

    access_token: str = create_access_token(data={"user_id": user.id})
    token: s.Token = s.Token(
        access_token=access_token,
        token_type="Bearer",
    )

    request_data: s.JobUpdate = s.JobUpdate(
        profession_id=job.profession_id,
        city=job.city,
        payment=job.payment,
        commission=job.commission,
        name=job.name,
        description=job.description,
        time=job.time,
        customer_first_name=job.customer_first_name,
        customer_last_name=job.customer_last_name,
        customer_phone=job.customer_phone,
        customer_street_address=job.customer_street_address,
        status=s.enums.JobStatus.JOB_IS_FINISHED,
    )
    response = client.put(
        f"api/job/{job.uuid}",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    db.refresh(job)
    assert job.status == s.enums.JobStatus.JOB_IS_FINISHED

    request_data: s.JobUpdate = s.JobUpdate(
        profession_id=job.profession_id,
        city=job.city,
        payment=job.payment,
        commission=job.commission,
        name=job.name,
        description=job.description,
        time=job.time,
        customer_first_name=job.customer_first_name,
        customer_last_name=job.customer_last_name,
        customer_phone=job.customer_phone,
        customer_street_address=job.customer_street_address,
        status=s.enums.JobStatus.JOB_IS_FINISHED,
    )
    response = client.put(
        f"api/job/{job.uuid}",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    job: m.Job = db.scalar(select(m.Job).where(m.Job.uuid == job.uuid))
    db.refresh(job)
    assert job.status == s.enums.JobStatus.JOB_IS_FINISHED


def test_patch_job(
    client: TestClient,
    db: Session,
):
    create_professions(db)
    create_jobs(db)
    fill_test_data(db)

    NEW_NAME = "TESTNAME JOBNAME"
    job: m.Job = db.scalar(
        select(m.Job).where(m.Job.status == s.enums.JobStatus.PENDING)
    )
    request_data: s.JobPatch = s.JobPatch(
        name=NEW_NAME, status=s.enums.JobStatus.IN_PROGRESS
    )
    user = job.owner

    access_token: str = create_access_token(data={"user_id": user.id})
    token: s.Token = s.Token(
        access_token=access_token,
        token_type="Bearer",
    )

    response = client.patch(
        f"api/job/{job.uuid}",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    db.refresh(job)
    assert response.status_code == status.HTTP_200_OK
    assert job.name == NEW_NAME
    assert job.status == s.enums.JobStatus.IN_PROGRESS

    request_data: s.JobPatch = s.JobPatch(
        customer_last_name=NEW_NAME + "1",
        status=s.enums.JobStatus.JOB_IS_FINISHED,
    )
    response = client.patch(
        f"api/job/{job.uuid}",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    job: m.Job = db.scalar(select(m.Job).where(m.Job.uuid == job.uuid))
    db.refresh(job)

    assert response.status_code == status.HTTP_200_OK
    assert job.customer_last_name == NEW_NAME + "1"
    assert job.status.value == request_data.status


def test_delete_job(
    client: TestClient,
    db: Session,
):
    create_professions(db)
    create_jobs(db)
    fill_test_data(db)

    job: m.Job = db.scalar(select(m.Job))

    user = job.owner

    access_token: str = create_access_token(data={"user_id": user.id})
    token: s.Token = s.Token(
        access_token=access_token,
        token_type="Bearer",
    )

    response = client.delete(
        f"api/job/{job.uuid}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )
    job: m.Job = db.scalar(select(m.Job).where(m.Job.uuid == job.uuid))
    db.refresh(job)
    assert response.status_code == status.HTTP_200_OK
    assert job.is_deleted
