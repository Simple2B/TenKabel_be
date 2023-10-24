from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sqlalchemy as sa

import app.schema as s
import app.model as m
from app.config import Settings, get_settings

from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_professions,
    create_locations,
    create_jobs,
    create_reviews,
)

settings: Settings = get_settings()


def test_tags_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_locations(db)
    create_professions(db)
    fill_test_data(db)
    create_jobs(db)
    create_reviews(db)

    response = client.get("api/tags/popular-tags")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == settings.POPULAR_TAGS_LIMIT

    user: m.User = db.scalar(
        sa.select(m.User).where(
            m.User.email == test_data.test_authorized_users[0].email
        )
    )

    response = client.get(
        "api/tags/",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(user.given_rates)
