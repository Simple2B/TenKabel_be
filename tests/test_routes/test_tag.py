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


def test_search_tags(
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

    tag: m.Tag = db.scalars(sa.select(m.Tag)).first()
    assert tag
    response = client.get(
        "api/tags/search",
        params={"q": tag.tag[0:2]},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    resp_obj = s.ListTagOut.parse_obj(response.json())
    assert resp_obj.items[0].tag[0:2] == tag.tag[0:2]

    response = client.get(
        "api/tags/search",
        params={"q": "some random random "},
    )
    assert response.status_code == status.HTTP_200_OK
    assert s.ListTagOut.parse_obj(response.json()).items == []

    tag = "test tag search"
    db.add(m.Tag(tag=tag, rate=s.BaseRate.RateStatus.POSITIVE))
    db.add(m.Tag(tag=tag, rate=s.BaseRate.RateStatus.NEGATIVE))
    db.commit()

    response = client.get(
        "api/tags/search",
        params={"q": tag},
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(s.ListTagOut.parse_obj(response.json()).items) == 1
