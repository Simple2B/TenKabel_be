from fastapi import status
from fastapi.testclient import TestClient
import sqlalchemy as sa
from sqlalchemy.orm import Session

import app.schema as s
import app.model as m
from app.utility import (
    fill_test_data,
    create_professions,
    create_jobs,
)
from tests.fixture import TestData


def test_auth(client: TestClient, db: Session, test_data: TestData):
    request_data = s.BaseUser(
        username=test_data.test_users[0].phone,
        email=test_data.test_users[0].email,
        password=test_data.test_users[0].password,
    )
    # login by username and password
    response = client.post("api/auth/login", data=request_data.dict())
    assert response and response.status_code == 200, "unexpected response"


def test_signup(client: TestClient, db: Session, test_data: TestData):
    request_data = s.BaseUser(
        username=test_data.test_user.username,
        email=test_data.test_user.email,
        password=test_data.test_user.password,
        phone=test_data.test_user.phone,
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response and response.status_code == 201
    assert db.execute(
        sa.select(m.User).where(m.User.email == test_data.test_user.email)
    ).one()

def test_user_jobs():
  ...
    
 

def test_get_user_profile(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):

    # create users
    fill_test_data(db)
    # create professions
    create_professions(db)
    # create jobs
    create_jobs(db)
    # get current jobs where user is worker
    response = client.get(
        "api/user/jobs",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    response = client.get(
        "api/user",
        headers={
            "Authorization": f"Bearer {authorized_users_tokens[0].access_token}",
        },
    )
    assert response.status_code == 200
    resp_obj: s.User = s.User.parse_obj(response.json())
    user: m.User = (
        db.query(m.User)
        .filter_by(email=test_data.test_authorized_users[0].email)
        .first()
    )
    assert user
    for job in resp_obj.jobs:
        assert job.worker_id == user.id

    # get current jobs where user is owner
    response = client.get(
        "api/user/postings",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())
    user = (
        db.query(m.User)
        .filter_by(email=test_data.test_authorized_users[0].email)
        .first()
    )
    assert user
    for job in resp_obj.jobs:
        assert job.owner_id == user.id
        
        
    assert resp_obj.uuid == user.uuid

    # get user by uuid
    response = client.get(
        f"api/user/{user.uuid}",
    )
