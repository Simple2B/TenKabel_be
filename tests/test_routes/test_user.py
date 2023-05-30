from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.schema as s
import app.model as m
from app.hash_utils import hash_verify

from tests.fixture import TestData
from tests.utility import (
    create_jobs,
    fill_test_data,
    create_professions,
)


def test_auth(client: TestClient, db: Session, test_data: TestData):
    # login by username and password
    response = client.post(
        "api/auth/login",
        data={
            "username": test_data.test_users[0].phone,
            "password": test_data.test_users[0].password,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_signup(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    request_data = s.UserSignUp(
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
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
    TEST_GOOGLE_MAIL = "somemail@gmail.com"
    request_data = s.GoogleAuthUser(
        email=TEST_GOOGLE_MAIL,
        photo_url="https://link_to_file/file.jpeg",
        uid="some-rand-uid",
        display_name="John Doe",
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    user: m.User = db.query(m.User).filter_by(email=TEST_GOOGLE_MAIL).first()
    assert user
    request_data = s.GoogleAuthUser(
        email=user.email,
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
    resp_obj: s.ListJob = s.ListJob.parse_obj(response.json())
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
    resp_obj: s.User = s.User.parse_obj(response.json())
    assert resp_obj.uuid == user.uuid
    assert resp_obj.positive_rates_count == user.positive_rates_count

    response = client.get(
        "api/user/rates",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK


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

    request_data: s.User = s.UserUpdate(
        username=user.email,
        first_name=test_data.test_authorized_users[1].first_name,
        last_name=test_data.test_authorized_users[1].last_name,
        email=user.email,
        phone=user.phone,
        professions=[1, 3],
    )
    response = client.put(
        "api/user",
        data=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user = (
        db.query(m.User)
        .filter_by(email=test_data.test_authorized_users[0].email)
        .first()
    )
    db.refresh(user)
    assert user.first_name == request_data.first_name
    assert user.last_name == request_data.last_name


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

    response = client.put(
        f"api/user/change-password?password={test_data.test_authorized_users[1].password}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    db.refresh(user)
    assert hash_verify(test_data.test_authorized_users[1].password, user.password)
