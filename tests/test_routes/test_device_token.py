from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from tests.fixture import TestData
import app.schema as s
import app.model as m

TEST_TOKEN = "TEST_RANDOM_TOKEN"


def test_device_token(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    # login by email and password
    request_data = s.BaseDeviceToken(token=TEST_TOKEN)
    response = client.post(
        "api/device-token",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    assert user
    assert db.scalar(select(m.DeviceToken).where(m.DeviceToken.user_id == user.id))
