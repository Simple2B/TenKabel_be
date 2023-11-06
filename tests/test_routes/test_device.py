from sqlalchemy import and_, select
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.utility import generate_uuid
import app.model as m

from tests.fixture.test_data import TestData


def test_add_device_to_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    faker,
):
    test_uuid = generate_uuid()
    test_push_token = "test_push_token"

    login_response = client.post(
        "api/auth/login-by-phone",
        json={
            "phone": test_data.test_users[0].phone,
            "password": test_data.test_users[0].password,
            "country_code": "IL",
        },
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    assert token is not None

    device_response = client.post(
        "api/devices",
        json={
            "uuid": test_uuid,
            "push_token": test_push_token,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert device_response.status_code == status.HTTP_200_OK

    device_query = select(m.Device).where(
        and_(
            m.Device.uuid == test_uuid,
            m.Device.push_token == test_push_token,
        )
    )

    device_in_db = db.scalar(device_query)

    assert device_in_db
    assert device_in_db.user.username == test_data.test_users[0].username

    new_push_token = "new_push_token"

    new_device_response = client.post(
        "api/devices",
        json={
            "uuid": test_uuid,
            "push_token": new_push_token,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert new_device_response.status_code == status.HTTP_200_OK

    new_device_query = select(m.Device).where(
        and_(
            m.Device.uuid == test_uuid,
            m.Device.push_token == new_push_token,
        )
    )

    device_in_db = db.scalar(new_device_query)

    assert device_in_db
    assert device_in_db.push_token == new_push_token
    assert device_in_db.user.username == test_data.test_users[0].username

    logout_response = client.post(
        "api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "device_uuid": test_uuid,
        },
    )
    assert logout_response.status_code == status.HTTP_200_OK
    device_in_db = db.scalar(device_query)

    assert device_in_db is None

    device_in_db = db.scalar(new_device_query)

    assert device_in_db is None
