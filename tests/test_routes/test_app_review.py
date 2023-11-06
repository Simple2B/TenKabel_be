from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

import app.model as m
import app.schema as s

from tests.fixture import TestData
from tests.utility import (
    create_locations,
    create_professions,
    fill_test_data,
)


def test_app_review_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_professions(db)
    create_locations(db)
    fill_test_data(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_authorized_users[0].phone)
    )

    request_data = s.AppReviewIn(stars_count=5, review=faker.text(max_nb_chars=1000))
    response = client.post(
        "api/app-review",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    app_review: m.AppReview = db.scalars(
        select(m.AppReview).where(m.AppReview.user_id == user.id)
    ).first()
    assert app_review
    resp_obj = s.AppReviewOut(**response.json())
    assert resp_obj.uuid == app_review.uuid

    response = client.get(
        f"api/app-review/{resp_obj.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_data = s.AppReviewOut(**response.json())
    assert resp_data.uuid == app_review.uuid
