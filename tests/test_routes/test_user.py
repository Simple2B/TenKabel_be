import base64
from datetime import datetime

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from pydantic.error_wrappers import ValidationError

import app.schema as s
import app.model as m
from app.hash_utils import hash_verify
from app.utility import generate_uuid

from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_jobs,
    create_professions,
    create_locations,
    create_applications,
    create_applications_for_user,
    create_rates,
    generate_customer_uid,
    create_jobs_for_user,
)


def test_auth(
    client: TestClient,
    db: Session,
    test_data: TestData,
    faker,
):
    # login by username and password

    response = client.post(
        "api/auth/login-by-phone",
        json={
            "phone": test_data.test_users[0].phone,
            "password": test_data.test_users[0].password,
            "country_code": "IL",
        },
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.post(
        "api/auth/login-by-phone",
        json={
            # testing wrong phone number (via whitespace)
            "username": test_data.test_users[0].phone[:-1]
            + " "
            + test_data.test_users[0].phone[-1],
            "password": test_data.test_users[0].password,
            "country_code": "IL",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_signup(
    client: TestClient,
    db: Session,
    monkeypatch,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    import httpx

    payplus_response = {
        "results": {
            "status": "success",
            "code": 0,
            "description": "operation has been success",
        },
        "data": {"customer_uid": generate_uuid()},
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return payplus_response

            @property
            def status_code(self):
                return status.HTTP_200_OK

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    create_professions(db)
    create_locations(db)
    TEST_PHONE_NUMBER = test_data.test_user.phone
    TEST_PHONE_WRONG_NUMBER = TEST_PHONE_NUMBER[:-1] + " " + TEST_PHONE_NUMBER[-1]
    TEST_PHONE_WRONG_NUMBER_LETTERS = "3123DASD211"

    try:
        request_data = s.UserSignUp(
            email=test_data.test_user.email,
            first_name=test_data.test_user.first_name,
            last_name=test_data.test_user.last_name,
            password=test_data.test_user.password,
            phone=TEST_PHONE_WRONG_NUMBER_LETTERS,
            profession_id=2,
            locations=[2, 3],
            country_code="IL",
        )
    except ValidationError:
        assert True
    else:
        assert False

    request_data = s.UserSignUp(
        email=test_data.test_user.email,
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
        password=test_data.test_user.password,
        phone=TEST_PHONE_NUMBER,
        profession_id=2,
        locations=[2, 3],
        country_code="IL",
    )

    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_409_CONFLICT

    try:
        request_data = s.UserSignUp(
            email=test_data.test_user.email,
            first_name=test_data.test_user.first_name,
            last_name=test_data.test_user.last_name,
            password=test_data.test_user.password,
            phone=TEST_PHONE_WRONG_NUMBER,
            profession_id=2,
            locations=[2, 3],
            country_code="IL",
        )
    except ValidationError:
        assert True
    else:
        assert False

    request_data = s.UserSignUp(
        email=test_data.test_user.email + ".us",
        first_name=test_data.test_user.first_name + "1",
        last_name=test_data.test_user.last_name + "1",
        password=test_data.test_user.password + "1",
        phone=TEST_PHONE_NUMBER[:-1] + "5",
        profession_id=2,
        locations=[2, 3],
        country_code="IL",
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED

    # checking if the user has created
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert user
    assert user.payplus_customer_uid

    assert user.professions[0].id == request_data.profession_id
    assert [location.id for location in user.locations] == request_data.locations

    # FINISH VERIFY
    response = client.put(
        "api/auth/verify",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_authorized_users[0].phone)
    )
    assert user.is_verified

    # pre-validating user exist
    response = client.get(
        f"api/auth/user/pre-validate?field=email&value={test_data.test_user.email}",
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    # pre-validating user exist
    response = client.get(
        f"api/auth/user/pre-validate?field=phone&value={test_data.test_user.phone}",
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    # pre-validating user not exist
    response = client.get(
        "api/auth/user/pre-validate?field=phone&value=123456",
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        "api/auth/user/pre-validate?field=phone&value=123456",
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.get(
        "api/auth/user/pre-validate?field=SOME_BAD_FIELD&value=123456",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_google_auth(
    client: TestClient,
    db: Session,
    monkeypatch,
    test_data: TestData,
    faker,
) -> None:
    import httpx

    payplus_response = {
        "results": {
            "status": "success",
            "code": 0,
            "description": "operation has been success",
        },
        "data": {"customer_uid": generate_uuid()},
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return payplus_response

            @property
            def status_code(self):
                return status.HTTP_200_OK

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    TEST_GOOGLE_MAIL = "somemail@gmail.com"
    request_data = s.GoogleAuthUser(
        email=TEST_GOOGLE_MAIL,
        first_name="John",
        last_name="Doe",
        photo_url="https://link_to_file/file.jpeg",
        uid="some-rand-uid",
        display_name="John Doe",
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token and resp_obj.minimum_mobile_app_version

    user: m.User = db.query(m.User).filter_by(email=TEST_GOOGLE_MAIL).first()
    assert user

    # test sign in
    request_data = s.GoogleAuthUser(
        email=user.email,
    ).dict()
    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.Token = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking non existing user
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert not user

    request_data = s.GoogleAuthUser(
        email=test_data.test_user.email,
        display_name=test_data.test_user.username,
        uid=test_data.test_user.google_openid_key,
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking if the user has created
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert user
    assert user.payplus_customer_uid

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK


def test_apple_auth(
    client: TestClient,
    db: Session,
    monkeypatch,
    test_data: TestData,
    faker,
) -> None:
    import httpx

    payplus_response = {
        "results": {
            "status": "success",
            "code": 0,
            "description": "operation has been success",
        },
        "data": {"customer_uid": generate_uuid()},
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return payplus_response

            @property
            def status_code(self):
                return status.HTTP_200_OK

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    TEST_APPLE_MAIL = "somemail@gmail.com"
    request_data = s.AppleAuthUser(
        email=TEST_APPLE_MAIL,
        phone="6635798512",
        uid="some-rand-uid",
        display_name="John Doe",
    ).dict()

    response = client.post("api/auth/apple", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    user: m.User = db.query(m.User).filter_by(email=TEST_APPLE_MAIL).first()
    assert user

    # test sign in
    request_data = s.AppleAuthUser(
        email=user.email,
    ).dict()
    response = client.post("api/auth/apple", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.Token = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking non existing user
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert not user

    request_data = s.AppleAuthUser(
        email=test_data.test_user.email,
        display_name=test_data.test_user.username,
        uid=test_data.test_user.google_openid_key,
    ).dict()

    response = client.post("api/auth/apple", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking if the user has created
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert user
    assert user.payplus_customer_uid

    response = client.post("api/auth/apple", json=request_data)
    assert response.status_code == status.HTTP_200_OK


def test_get_user_profile(
    client: TestClient,
    db: Session,
    test_data: TestData,
    monkeypatch,
    authorized_users_tokens: list[s.Token],
    faker,
):
    import httpx

    payplus_response = {
        "results": {
            "status": "success",
            "code": 0,
            "description": "operation has been success",
        },
        "data": {
            "card_uid": generate_uuid(),
        },
    }

    def mock_post(*args, **kwargs):
        class MockResponse:
            def json(self):
                return payplus_response

            @property
            def status_code(self):
                return status.HTTP_200_OK

        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    create_jobs(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )

    create_applications(db)
    create_applications_for_user(db, user.id)
    create_jobs_for_user(db, user.id, 15)
    create_rates(db)

    response = client.get(
        "api/users/jobs",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    for job in resp_obj.jobs:
        assert user.id in (job.worker_id, job.owner_id)

    response = client.get(
        "api/users/jobs",
        params={"manage_tab": s.Job.TabFilter.PENDING.value},
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    jobs_ids = db.scalars(
        select(m.Application.job_id).where(
            or_(
                m.Application.worker_id == user.id,
            )
        )
    ).all()
    query = select(m.Job).filter(
        and_(
            or_(m.Job.id.in_(jobs_ids), m.Job.owner_id == user.id),
            m.Job.status == s.enums.JobStatus.PENDING,
            m.Job.is_deleted.is_(False),
        )
    )
    jobs = db.scalars(query).all()

    assert len(jobs) == len(resp_obj.jobs)
    for job in resp_obj.jobs:
        assert job.id in [j.id for j in jobs]
        assert job.status == s.enums.JobStatus.PENDING.value
        if job.owner_id != user.id:
            assert user.id in [
                application.worker_id for application in job.applications
            ]

    response = client.get(
        "api/users/jobs",
        params={"manage_tab": s.Job.TabFilter.ACTIVE.value},
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    query = select(m.Job).filter(
        and_(
            or_(m.Job.worker_id == user.id, m.Job.owner_id == user.id),
            m.Job.is_deleted.is_(False),
            and_(
                m.Job.is_deleted.is_(False),
                or_(
                    m.Job.status == s.enums.JobStatus.IN_PROGRESS,
                    and_(
                        m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED,
                        or_(
                            m.Job.payment_status == s.enums.PaymentStatus.UNPAID,
                            m.Job.commission_status == s.enums.CommissionStatus.UNPAID,
                        ),
                    ),
                ),
            ),
        )
    )

    jobs = db.scalars(query).all()

    assert len(jobs) == len(resp_obj.jobs)

    for job in resp_obj.jobs:
        assert job.id in [j.id for j in jobs]
        assert job.status in (
            s.enums.JobStatus.IN_PROGRESS.value,
            s.enums.JobStatus.JOB_IS_FINISHED,
        )
        assert (
            job.payment_status == s.enums.PaymentStatus.UNPAID.value
            or job.commission_status == s.enums.CommissionStatus.UNPAID.value
            or job.status == s.enums.JobStatus.IN_PROGRESS.value
        )
        assert user.id in (job.owner_id, job.worker_id)

    response = client.get(
        "api/users/jobs",
        params={"manage_tab": s.Job.TabFilter.ARCHIVE.value},
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    query = select(m.Job).filter(
        and_(
            or_(m.Job.worker_id == user.id, m.Job.owner_id == user.id),
            or_(
                m.Job.is_deleted.is_(True),
                and_(
                    m.Job.payment_status == s.enums.PaymentStatus.PAID,
                    m.Job.commission_status == s.enums.CommissionStatus.PAID,
                    m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED,
                ),
            ),
        )
    )
    jobs = db.scalars(query).all()

    for job in resp_obj.jobs:
        assert int(job.id) in [j.id for j in jobs]
        assert job.is_deleted or (
            job.payment_status == s.enums.PaymentStatus.PAID.value
            and job.commission_status == s.enums.CommissionStatus.PAID.value
        )
        assert user.id in (job.owner_id, job.worker_id)

    response = client.get(
        "api/users",
        headers={
            "Authorization": f"Bearer {authorized_users_tokens[0].access_token}",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.User = s.User.parse_obj(response.json())
    user: m.User = db.scalar(
        select(m.User).filter_by(email=test_data.test_authorized_users[0].email)
    )
    db.refresh(user)
    assert user.id == resp_obj.id
    assert user.picture == resp_obj.picture
    # get current jobs where user is owner
    response = client.get(
        "api/users/postings",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.ListJob = s.ListJob.parse_obj(response.json())

    for job in resp_obj.jobs:
        assert job.owner_id == user.id

    # get user by uuid
    response = client.get(
        f"api/users/{user.uuid}",
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.User = s.User.parse_obj(response.json())
    assert resp_obj.uuid == user.uuid
    assert resp_obj.positive_rates_count == user.positive_rates_count

    response = client.get(
        "api/users/rates",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.RateList = s.RateList.parse_obj(response.json())
    for rate in resp_obj.rates:
        assert rate.owner_id == user.id

    response = client.get(
        "api/users/applications?type=owner",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    resp_obj: s.ApplicationList = s.ApplicationList.parse_obj(response.json())
    for rate in resp_obj.applications:
        assert rate.owner_id == user.id

    card_data = s.CardIn(
        credit_card_number="1234567890123456",
        card_date_mmyy=datetime(2021, 12, 1),
        card_name="test",
    )

    generate_customer_uid(user, db)

    response = client.post(
        "api/users/payplus-token",
        json=jsonable_encoder(card_data),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    assert user.payplus_card_uid is not None
    assert user.card_name == card_data.card_name


def test_update_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    fill_test_data(db)
    create_professions(db)
    create_locations(db)
    create_jobs(db)

    PROFESSION_IDS = [1, 3]
    LOCATIONS_IDS = [1, 4]

    with open("./test_image.png", "rb") as f:
        PICTURE = base64.b64encode(f.read()).decode("utf-8")

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    request_data: s.UserUpdate = s.UserUpdate(
        username=user.email,
        first_name=test_data.test_authorized_users[1].first_name + "A1",
        last_name=test_data.test_authorized_users[1].last_name,
        email=user.email,
        phone=user.phone,
        picture=PICTURE,
        professions=PROFESSION_IDS,
        locations=LOCATIONS_IDS,
        country_code="IL",
    )

    response = client.patch(
        "api/users",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    db.refresh(user)

    assert user.first_name == request_data.first_name
    assert user.last_name == request_data.last_name
    assert user.picture == PICTURE
    assert len(user.professions) == len(PROFESSION_IDS)
    for profession in user.professions:
        assert profession.id in PROFESSION_IDS


def test_notifications_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    fill_test_data(db)
    create_locations(db)
    create_professions(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    request_data: s.UserNotificationSettingsIn = s.UserNotificationSettingsIn(
        notification_profession=[1],
        notification_locations=[1, 3],
        notification_job_status=False,
    )
    response = client.patch(
        "api/users/notification-settings",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK

    db.refresh(user)
    assert user.notification_job_status == request_data.notification_job_status
    assert [
        profession.id for profession in user.notification_profession
    ] == request_data.notification_profession
    assert [
        location.id for location in user.notification_locations
    ] == request_data.notification_locations


def test_passwords(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_professions(db)
    create_jobs(db)
    fill_test_data(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    assert user
    TEST_NEW_PASSWORD = "TEST_NEW_PASSWORD"
    # ForgotPassword
    request_data = s.ForgotPassword(
        new_password=TEST_NEW_PASSWORD, phone=user.phone, country_code="IL"
    )
    response = client.post(
        "api/users/forgot-password",
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(user)
    assert hash_verify(request_data.new_password, user.password)

    TEST_NEW_FORGOT_PASSWORD = TEST_NEW_PASSWORD + "abc"
    request_data = s.ChangePassword(
        current_password=TEST_NEW_PASSWORD,
        new_password=TEST_NEW_FORGOT_PASSWORD,
    )
    response = client.post(
        "api/users/change-password",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(user)
    assert hash_verify(TEST_NEW_FORGOT_PASSWORD, user.password)


def test_delete_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    create_professions(db)
    create_locations(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    uuid = generate_uuid()
    push_token = "test_token"
    request_data = s.DeviceIn(uuid=uuid, push_token=push_token)

    response = client.post(
        "api/devices",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_200_OK

    request_data = s.LogoutIn(device_uuid=push_token)
    response = client.request(
        "DELETE",
        "api/users",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        content=request_data.json(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert user.is_deleted

    # check for negative case
    user.is_deleted = False
    db.commit()
    create_jobs_for_user(db, user.id)

    response = client.request(
        "DELETE",
        "api/users",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        content=request_data.json(),
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert not user.is_deleted
