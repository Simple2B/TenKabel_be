import base64
import re

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_
from pydantic.error_wrappers import ValidationError

import app.schema as s
import app.model as m
from app.hash_utils import hash_verify

from tests.fixture import TestData
from tests.utility import (
    create_jobs,
    fill_test_data,
    create_professions,
    create_locations,
    create_applications,
    create_jobs_for_user,
    create_applications_for_user,
)


def test_auth(client: TestClient, db: Session, test_data: TestData):
    # login by username and password
    response = client.post(
        "api/auth/login",
        data={
            # testing wrong phone number (via whitespace)
            "username": test_data.test_users[0].phone[:-1]
            + " "
            + test_data.test_users[0].phone[-1],
            "password": test_data.test_users[0].password,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post(
        "api/auth/login",
        data={
            "username": test_data.test_users[0].phone,
            "password": test_data.test_users[0].password,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    user = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_users[0].phone)
    )
    user.is_verified = True
    db.commit()

    response = client.post(
        "api/auth/login-by-phone",
        json={
            "phone": test_data.test_users[0].phone,
            "password": test_data.test_users[0].password,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_signup(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    create_professions(db)
    create_locations(db)
    TEST_PHONE_NUMBER = test_data.test_user.phone
    TEST_PHONE_WRONG_NUMBER = TEST_PHONE_NUMBER[:-1] + " " + TEST_PHONE_NUMBER[-1]
    TEST_PHONE_WRONG_NUMBER_LETTERS = "3123DASD211"

    try:
        request_data = s.UserSignUp(
            first_name=test_data.test_user.first_name,
            last_name=test_data.test_user.last_name,
            password=test_data.test_user.password,
            phone=TEST_PHONE_WRONG_NUMBER_LETTERS,
            profession_id=2,
            locations=[2, 3],
        )
    except ValidationError:
        assert True
    else:
        assert False

    request_data = s.UserSignUp(
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
        password=test_data.test_user.password,
        phone=TEST_PHONE_NUMBER,
        profession_id=2,
        locations=[2, 3],
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_409_CONFLICT

    try:
        request_data = s.UserSignUp(
            first_name=test_data.test_user.first_name,
            last_name=test_data.test_user.last_name,
            password=test_data.test_user.password,
            phone=TEST_PHONE_WRONG_NUMBER,
            profession_id=2,
            locations=[2, 3],
        )
    except ValidationError:
        assert True
    else:
        assert False

    request_data = s.UserSignUp(
        first_name=test_data.test_user.first_name + "1",
        last_name=test_data.test_user.last_name + "1",
        password=test_data.test_user.password + "1",
        phone=TEST_PHONE_NUMBER[:-1] + "5",
        profession_id=2,
        locations=[2, 3],
    )
    response = client.post("api/auth/sign-up", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED

    user: m.User = db.scalar(
        select(m.User).where(m.User.phone == test_data.test_user.phone)
    )
    assert user
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


def test_google_auth(client: TestClient, db: Session, test_data: TestData) -> None:
    TEST_GOOGLE_MAIL = "somemail@gmail.com"
    request_data = s.GoogleAuthUser(
        email=TEST_GOOGLE_MAIL,
        photo_url="https://link_to_file/file.jpeg",
        uid="some-rand-uid",
        display_name="John Doe",
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    user: m.User = db.query(m.User).filter_by(email=TEST_GOOGLE_MAIL).first()
    assert user
    assert re.search(r"^(http|https)://", user.picture)

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

    request_data = s.BaseUser(
        email=test_data.test_user.email,
        password=test_data.test_user.password,
        username=test_data.test_user.username,
        first_name=test_data.test_user.first_name,
        last_name=test_data.test_user.last_name,
        google_openid_key=test_data.test_user.google_openid_key,
        picture=test_data.test_user.picture,
        phone=test_data.test_user.phone,
    ).dict()

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Token.parse_obj(response.json())
    assert resp_obj.access_token

    # checking if the user has created
    user = db.query(m.User).filter_by(email=test_data.test_user.email).first()
    assert user

    response = client.post("api/auth/google", json=request_data)
    assert response.status_code == status.HTTP_200_OK


def test_get_user_profile(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    create_jobs_for_user(db, user.id)
    create_applications(db)
    create_applications_for_user(db, user.id)

    # get current jobs where user is worker
    response = client.get(
        "api/user/jobs",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    for job in resp_obj.jobs:
        assert user.id in (job.worker_id, job.owner_id)

    response = client.get(
        "api/user/jobs",
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
            m.Job.status == s.Job.Status.PENDING,
        )
    )
    jobs = db.scalars(query).all()

    assert len(jobs) == len(resp_obj.jobs)
    for job in resp_obj.jobs:
        assert job.id in [j.id for j in jobs]
        assert job.status == s.Job.Status.PENDING.value
        if job.owner_id != user.id:
            assert user.id in [
                application.worker_id for application in job.applications
            ]

    response = client.get(
        "api/user/jobs",
        params={"manage_tab": s.Job.TabFilter.ACTIVE.value},
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    query = select(m.Job).filter(
        and_(
            or_(m.Job.worker_id == user.id, m.Job.owner_id == user.id),
            or_(
                m.Job.status == s.Job.Status.IN_PROGRESS,
                m.Job.status == s.Job.Status.APPROVED,
            ),
        )
    )
    jobs = db.scalars(query).all()

    assert len(jobs) == len(resp_obj.jobs)

    for job in resp_obj.jobs:
        assert job.id in [j.id for j in jobs]
        assert job.status in (
            s.Job.Status.IN_PROGRESS.value,
            s.Job.Status.APPROVED.value,
        )
        assert user.id in (job.owner_id, job.worker_id)

    response = client.get(
        "api/user/jobs",
        params={"manage_tab": s.Job.TabFilter.ARCHIVE.value},
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ListJob.parse_obj(response.json())

    query = select(m.Job).filter(
        and_(
            or_(m.Job.worker_id == user.id, m.Job.owner_id == user.id),
            m.Job.status == s.Job.Status.JOB_IS_FINISHED,
        )
    )
    jobs = db.scalars(query).all()

    for job in resp_obj.jobs:
        assert int(job.id) in [j.id for j in jobs]
        assert job.status == s.Job.Status.JOB_IS_FINISHED.value
        assert user.id in (job.owner_id, job.worker_id)

    response = client.get(
        "api/user",
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
        "api/user/postings",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.ListJob = s.ListJob.parse_obj(response.json())

    for job in resp_obj.jobs:
        assert job.owner_id == user.id

    # get user by uuid
    response = client.get(
        f"api/user/{user.uuid}",
    )
    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.User = s.User.parse_obj(response.json())
    assert resp_obj.uuid == user.uuid
    assert resp_obj.positive_rates_count == user.positive_rates_count

    response = client.get(
        "api/user/rates",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    resp_obj: s.RateList = s.RateList.parse_obj(response.json())
    for rate in resp_obj.rates:
        assert rate.worker_id == user.id

    response = client.get(
        "api/user/applications?type=owner",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    resp_obj: s.ApplicationList = s.ApplicationList.parse_obj(response.json())
    for rate in resp_obj.applications:
        assert rate.owner_id == user.id


def test_update_user(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    with open("./test_image.png", "rb") as f:
        PICTURE = base64.b64encode(f.read())

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    request_data: s.User = s.UserUpdate(
        username=user.email,
        first_name=test_data.test_authorized_users[1].first_name,
        last_name=test_data.test_authorized_users[1].last_name,
        email=user.email,
        phone=user.phone,
        picture=PICTURE,
        professions=[1, 3],
    )

    response = client.put(
        "api/user",
        data=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    user = (
        db.query(m.User)
        .filter_by(email=test_data.test_authorized_users[0].email)
        .first()
    )
    db.refresh(user)
    assert user.picture == PICTURE
    assert user.first_name == request_data.first_name
    assert user.last_name == request_data.last_name


def test_passwords(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)

    user: m.User = db.scalar(
        select(m.User).where(
            m.User.username == test_data.test_authorized_users[0].username
        )
    )

    assert user
    TEST_NEW_PASSWORD = "TEST_NEW_PASSWORD"
    # ForgotPassword
    request_data = s.ForgotPassword(new_password=TEST_NEW_PASSWORD, phone=user.phone)
    response = client.post(
        "api/user/forgot-password",
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
        "api/user/change-password",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(user)
    assert hash_verify(TEST_NEW_FORGOT_PASSWORD, user.password)


# def test_upload_avatar(
#     client: TestClient,
#     db: Session,
#     mock_google_cloud_storage,
#     test_data: TestData,
#     authorized_users_tokens: list,
# ):
#     # Create a mock client
#     response = client.post(
#         "api/user/upload-avatar",
#         files={
#             "profile_avatar": open("tests/test_image.png", "rb"),
#         },
#         headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
#     )
#     assert response.status_code == status.HTTP_201_CREATED
#     assert (
#         db.query(m.User)
#         .filter_by(email=test_data.test_authorized_users[0].email)
#         .picture
#     )
