from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.schema as s
import app.model as m
from tests.fixture import TestData


def test_auth(
    client: TestClient,
    test_data: TestData,
):
    request_data = s.BaseUser(
        username=test_data.test_users[0].username,
        email=test_data.test_users[0].email,
        password=test_data.test_users[0].password,
    )
    # login by username and password
    response = client.post("api/auth/login", data=request_data.dict())
    assert response and response.status_code == 200, "unexpected response"


def test_signup(
    client: TestClient,
    db: Session,
    test_data: TestData,
):
    request_data = s.BaseUser(
        username=test_data.test_user.username,
        email=test_data.test_user.email,
        password=test_data.test_user.password,
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response and response.status_code == 201
    assert db.query(m.User).filter_by(email=test_data.test_user.email)


def test_google_auth(
    client: TestClient,
    test_data: TestData,
):
    request_data = s.BaseUserGoogle(
        username=test_data.test_user.username,
        email=test_data.test_user.email,
        google_openid="TEST_GOOGLE_OPENID_KEY",
    )
    # login by username and password
    response = client.post("api/auth/google-oauth", json=request_data.dict())
    assert response and response.status_code == 200, "unexpected response"


def test_user_phone_confirmation(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens,
):
    request_data = s.UserProfile(
        first_name=test_data.test_users[0].username,
        last_name=test_data.test_users[0].email,
        password=test_data.test_users[0].password,
        phone_number="1112223334444",
    )
    response = client.post(
        "api/user/phone-confirmation",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response and response.status_code == 200, "unexpected response"
    user = db.query(m.User).filter_by(email=test_data.test_users[0].email).first()
    assert user
    assert user.phone_number == request_data.phone_number
    assert user.last_name == request_data.last_name
