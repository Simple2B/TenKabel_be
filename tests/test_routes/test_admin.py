from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest

from tests.fixture import TestData


@pytest.mark.skip(reason="Flow of payment has been changed")
def test_admin_auth(
    client: TestClient,
    db: Session,
    test_data: TestData,
    faker,
):
    # login by email and password
    TEST_SU_EMAIL = "test_superuser@gmail.com"
    TEST_SU_PASSWORD = "test_su_password"
    su_data = {
        "email": TEST_SU_EMAIL,
        "password": TEST_SU_PASSWORD,
    }
    response = client.post("admin/login", data=su_data)
    assert response and response.status_code == 200
