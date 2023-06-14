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
)


def test_application_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    fill_test_data(db)
    create_professions(db)
    create_jobs(db)
    create_applications(db)

    job_id: int | None = db.scalar(
        select(m.Job.id).where((m.Job.status == s.enums.Status.PENDING))
    )
    auth_user_id = db.scalar(
        select(m.User.id).where(
            m.User.email == test_data.test_authorized_users[0].email
        )
    )

    request_data: s.ApplicationIn = s.ApplicationIn(job_id=job_id)

    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_409_CONFLICT)

    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    # TODO: check this test for 404 error
    # non_exist_job_id = 321312
    # request_data: s.ApplicationIn = s.ApplicationIn(job_id=non_exist_job_id)
    # response = client.post(
    #     "api/application",
    #     headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    #     json=request_data.dict(),
    # )
    # assert response.status_code == status.HTTP_404_NOT_FOUND

    application: m.Application = db.scalar(
        select(m.Application).where(
            (m.Application.job_id == job_id)
            and (m.Application.worker_id == auth_user_id)
        )
    )

    assert application

    request_data = s.BaseApplication(
        owner_id=application.owner_id,
        worker_id=application.worker_id,
        job_id=application.job_id,
        status=s.BaseApplication.ApplicationStatus.ACCEPTED,
    )

    response = client.put(
        f"api/application/{application.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(application)
    assert application.status == s.BaseApplication.ApplicationStatus.ACCEPTED

    job = db.scalar(select(m.Job).where(m.Job.id == application.job_id))
    assert (
        job.status == s.enums.Status.APPROVED and job.worker_id == application.worker_id
    )
    applications = db.scalars(
        select(m.Application).where((m.Application.job_id == application.job_id))
    ).all()

    for exist_application in applications:
        if exist_application.id != application.id:
            assert (
                exist_application.status == s.BaseApplication.ApplicationStatus.DECLINED
            )
