from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder

import app.schema as s
import app.model as m

from tests.fixture import TestData
from tests.utility import (
    create_jobs,
    fill_test_data,
    create_professions,
)


def test_auth(client: TestClient, db: Session, test_data: TestData):
    request_data = s.BaseUser(
        username=test_data.test_users[0].phone,
        first_name=test_data.test_users[0].first_name,
        last_name=test_data.test_users[0].last_name,
        email=test_data.test_users[0].email,
        password=test_data.test_users[0].password,
    )
    # login by username and password
    response = client.post("api/auth/login", data=request_data.dict())
    assert response.status_code == 200, "unexpected response"


def test_signup(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    request_data = s.BaseUser(
        username=test_data.test_user.username,
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
        email=test_data.test_user.email,
        password=test_data.test_user.password,
        phone=test_data.test_user.phone,
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED
    user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    assert user
    assert not user.is_verified

    response = client.put(
        "api/auth/verify",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    db.refresh(user)
    assert user.is_verified


def test_google_auth(client: TestClient, db: Session, test_data: TestData) -> None:
    user: m.User = (
        db.query(m.User).filter_by(email=test_data.test_users[0].email).first()
    )
    assert user

    request_data = s.BaseUser(
        email=user.email,
        password=test_data.test_users[0].password,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        google_openid_key=user.google_openid_key,
        picture=user.picture,
        phone=user.phone,
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking non existing user
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert not user

    request_data = s.BaseUser(
        email=test_data.test_user.email,
        password=test_data.test_user.password,
        username=test_data.test_user.username,
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
        google_openid_key=test_data.test_user.google_openid_key,
        picture=test_data.test_user.picture,
        phone=test_data.test_user.phone,
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking if the user has created
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert user

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK


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

    # get user by uuid
    response = client.get(
        f"api/user/{user.uuid}",
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.User.parse_obj(response.json())
    assert resp_obj.uuid == user.uuid


def test_update_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    request_data: s.User = s.User(
        professions=user.professions,
        id=user.id,
        uuid=user.uuid,
        jobs_completed_count=user.jobs_completed_count,
        jobs_posted_count=user.jobs_posted_count,
        created_at=user.created_at,
        username=user.username,
        first_name=user.first_name + "test",
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        picture=user.picture,
        google_openid_key=user.google_openid_key,
        password=user.password,
        is_verified=user.is_verified,
    )

    response = client.put(
        "api/user",
        json=jsonable_encoder(request_data),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    db.refresh(user)
    assert user.first_name == request_data.first_name


def test_password_update(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    assert user

    response = client.post(
        f"api/user/check-password?password={test_data.test_authorized_users[0].password}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
