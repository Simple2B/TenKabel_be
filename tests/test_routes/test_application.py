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
)


def test_application_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    request_data = s.BaseApplication(
        owner_id=test_data.test_application.owner_id,
        worker_id=test_data.test_application.worker_id,
    )

    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED

    applications = db.scalars(
        select(m.Application).where(
            (m.Application.status == test_data.test_application.status)
            and (m.Application.owner_id == test_data.test_application.owner_id)
            and (m.Application.worker_id == test_data.test_application.worker_id)
        )
    ).all()

    assert len(applications) == 1

    request_data.status = s.BaseApplication.Status.ACCEPTED
    response = client.put(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
