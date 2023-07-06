from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
import pytest

import app.schema as s
import app.model as m
from app.controller.platform_payment import collect_fee
from app.config import Settings, get_settings

from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_professions,
    create_jobs,
    create_jobs_for_user,
    create_applications_for_user,
    generate_card_token,
)


@pytest.mark.skip(reason="Flow of payment has been changed")
def test_payplus_form_url(
    client: TestClient,
    db: Session,
    monkeypatch,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    import httpx

    fill_test_data(db)
    create_professions(db)
    create_jobs(db)
    auth_user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    assert auth_user
    create_jobs_for_user(db, auth_user.id, 20)

    payplus_response = {
        "results": {
            "status": "success",
            "code": 0,
            "description": "payment page link is been generated",
        },
        "data": {
            "page_request_uid": "f33f7a1f-5ea7-4857-992a-2da95b369f53",
            "payment_page_link": "https://payments.payplus.co.il/some-payment-link",
            "qr_code_image": "https://payments.payplus.co.il/some-payment-link-qr-code",
        },
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):  # noqa: F811
                return payplus_response

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)
    response = client.get(
        f"api/payment/form-url/{auth_user.jobs_owned[0].uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    form_url = s.PlatformPaymentLinkOut.parse_obj(response.json())
    assert str(form_url.url) == payplus_response["data"]["payment_page_link"]


def test_payment_flow(
    client: TestClient,
    db: Session,
    monkeypatch,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    settings: Settings = get_settings(),
):
    import httpx

    # Mocking request to payplus
    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):  # noqa: F811
                return {"some": "message"}

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)
    fill_test_data(db)
    create_professions(db)

    auth_user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    create_jobs_for_user(db, auth_user.id, 20)
    create_applications_for_user(db, auth_user.id)
    for user in db.scalars(select(m.User)):
        generate_card_token(user, db)
        generate_card_token(user, db)

    application = db.scalar(
        select(m.Application).where(m.Application.owner_id == auth_user.id)
    )
    request_data = s.BaseApplication(
        owner_id=application.owner_id,
        worker_id=application.worker_id,
        job_id=application.job_id,
        status=s.Application.ApplicationStatus.ACCEPTED,
    )
    # first lets create platform payments and platform comissions
    response = client.put(
        f"api/application/{application.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED

    # testing collect_fee() method
    collect_fee()
