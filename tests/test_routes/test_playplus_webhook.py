from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx

import app.schema as s
import app.model as m


from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_professions,
    create_jobs,
    create_jobs_for_user,
)


def test_payplus_form_url(
    client: TestClient,
    db: Session,
    monkeypatch,
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
            def json(self):
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


# def test_payplus_webhook(
#     client: TestClient,
#     db: Session,
#     test_data: TestData,
#     authorized_users_tokens: list[s.Token],
# ):
#     fill_test_data(db)
#     create_professions(db)
#     create_jobs(db)
#     auth_user: m.User = db.scalar(
#         select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
#     )
#     assert auth_user
#     create_jobs_for_user(db, auth_user.id, 20)
#     request_data = {}
#     response = client.post(
#         "api/payment/webhook",
#         json=request_data,
#     )
#     assert response.status_code == status.HTTP_200_OK
