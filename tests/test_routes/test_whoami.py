from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import status


from tests.fixture.test_data import TestData
import app.model as m
import app.schema as s


def test_who_am_i(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_authorized_users[0].phone)
    )
    response = client.get(
        "api/whoami/user",
        headers={
            "Authorization": f"Bearer {authorized_users_tokens[0].access_token}",
            "App-Version": "1.0.0",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.WhoAmIOut = s.WhoAmIOut.parse_obj(response.json())
    assert resp_obj.uuid == user.uuid
