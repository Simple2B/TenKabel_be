from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.schema as s
import app.model as m


from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_professions,
    create_jobs,
    create_jobs_for_user,
)


def test_payplus_webhook(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)
    auth_user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    assert auth_user
    create_jobs_for_user(db, auth_user.id, 20)
    request_data = {}
    response = client.post(
        "api/payment/webhook",
        json=request_data,
    )
    assert response.status_code == status.HTTP_200_OK
