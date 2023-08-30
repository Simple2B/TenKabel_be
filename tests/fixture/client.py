from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.schema as s
from app.controller.push_notification import PushHandler
from .test_data import TestData


@pytest.fixture
def client(monkeypatch) -> Generator:
    from app.main import app

    class PushNotificationMock:
        _is_initialized = False

        def __init__(self) -> None:
            pass

        def send_notification(*args, **kwargs):
            return

    with TestClient(app) as c:
        monkeypatch.setattr(PushHandler, "__init__", PushNotificationMock.__init__)
        monkeypatch.setattr(
            PushHandler, "send_notification", PushNotificationMock.send_notification
        )

        yield c


@pytest.fixture
def authorized_users_tokens(
    client: TestClient,
    db: Session,
    test_data: TestData,
) -> Generator[list[s.Token], None, None]:
    tokens = []
    for user in test_data.test_authorized_users:
        response = client.post(
            "api/auth/login-by-phone",
            json={
                "phone": user.phone,
                "password": user.password,
                "country_code": user.country_code,
            },
        )

        assert response.status_code == 200
        token = s.Token.parse_obj(response.json())
        tokens += [token]
    yield tokens


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return "some-seed-tenkabel"
