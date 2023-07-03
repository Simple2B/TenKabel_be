from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select
import pytest

import app.schema as s
import app.model as m
from app.controller import collect_fee
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
    collect_fee(db, settings)

    # request_data = {
    #     "data": {
    #         "items": [
    #             {
    #                 "vat": 0.04,
    #                 "name": "General Product - מוצר כללי",
    #                 "barcode": "000000000",
    #                 "quantity": 1,
    #                 "amount_pay": 0.26,
    #                 "product_uid": "some-random-product-id",
    #                 "discount_type": None,
    #                 "discount_value": None,
    #                 "quantity_price": 0.22,
    #                 "discount_amount": 0,
    #             }
    #         ],
    #         "cashier_name": "cashier-01-test",
    #         "customer_uid": "some-customer-id",
    #         "terminal_uid": "some-terminal-id",
    #         "customer_email": "sample@domain.com",
    #         "card_information": {
    #             "token": "b09021bb-01c9-428a-bb61-27d57a5f729c9844",
    #             "brand_id": 1,
    #             "card_bin": "532614",
    #             "issuer_id": 1,
    #             "clearing_id": 1,
    #             "expiry_year": "26",
    #             "four_digits": "9844",
    #             "card_foreign": 0,
    #             "expiry_month": "05",
    #             "token_number": "HMpI3lxaBe",
    #             "card_holder_name": "Bohdan ",
    #             "identification_number": "",
    #         },
    #     },
    #     "transaction": {
    #         "rrn": 154515,
    #         "uid": "some-transaction-id",
    #         "date": datetime.now().isoformat(),
    #         "type": "payment_page",
    #         "amount": 0.26,
    #         "number": "some-transcation-number",
    #         "paramj": 4,
    #         "uid_emv": 11111111111000023000,
    #         "add_data": None,
    #         "currency": "USD",
    #         "payments": {
    #             "number_of_payments": 1,
    #             "first_payment_amount": 0,
    #             "rest_payments_amount": 0,
    #         },
    #         "secure3D": {"status": None, "tracking": None},
    #         "more_info": None,
    #         "more_info_1": json.dumps(
    #             {
    #                 "platform_payment_uuid": auth_user.uuid,
    #             }
    #         ),
    #         "more_info_2": None,
    #         "more_info_3": None,
    #         "more_info_4": None,
    #         "more_info_5": None,
    #         "status_code": "000",
    #         "credit_terms": "regular",
    #         "voucher_number": "22-365-77",
    #         "approval_number": "0621514D",
    #         "payment_page_request_uid": "5456ccc9-2862-4862-84ae-947163778d40",
    #         "original_amount_currency_dcc": None,
    #     },
    #     "transaction_type": "Charge",
    # }
    # response = client.post(
    #     "api/payment/webhook",
    #     json=request_data,
    # )
    # assert response.status_code == status.HTTP_200_OK
    # platform_payment = db.scalar(
    #     select(m.PlatformComission).where(
    #         m.PlatformComission.user_id == auth_user.id,
    #         m.PlatformComission.job_id == auth_user.jobs_owned[0].id,
    #     )
    # )
    # assert platform_payment.status == s.enums.PlatformPaymentStatus.PAID
    # assert platform_payment.transaction_number == request_data["transaction"]["number"]
