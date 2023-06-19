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
    create_applications,
    create_notifications,
)


def test_notification_get_list(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    create_professions(db)
    fill_test_data(db)
    create_jobs(db)
    create_applications(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    response = client.get(
        "api/notification/notifications",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.NotificationList.parse_obj(response.json())
    assert len(resp_obj.items) == len(test_data.test_notifications_applications) + len(
        test_data.test_notifications_jobs
    )
    for item in resp_obj.items:
        assert item.user_id == user.id
