from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

import app.schema as s
import app.model as m

from tests.fixture import TestData
from tests.utility import (
    fill_test_data,
    create_professions,
    create_jobs,
    generate_customer_uid,
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

    job_id: int | None = db.scalar(
        select(m.Job.id).where((m.Job.status == s.enums.JobStatus.PENDING))
    )
    auth_user = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )

    request_data: s.ApplicationIn = s.ApplicationIn(job_id=job_id)

    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    generate_customer_uid(auth_user, db)
    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED

    application: m.Application = db.scalar(
        select(m.Application).where(
            (m.Application.job_id == job_id)
            and (m.Application.worker_id == auth_user.id)
        )
    )

    assert db.scalar(
        select(m.Notification).where(
            and_(
                m.Notification.entity_id == application.id,
                m.Notification.type == s.NotificationType.APPLICATION_CREATED,
            )
        )
    )

    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    non_exist_job_id = 321312
    request_data: s.ApplicationIn = s.ApplicationIn(job_id=non_exist_job_id)
    response = client.post(
        "api/application",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    request_data = s.ApplicationPatch(
        status=s.BaseApplication.ApplicationStatus.DECLINED,
    )

    response = client.patch(
        f"api/application/{application.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(application)
    assert application.status == s.BaseApplication.ApplicationStatus.DECLINED

    request_data = s.BaseApplication(
        owner_id=application.owner_id,
        worker_id=application.worker_id,
        job_id=application.job_id,
        status=s.BaseApplication.ApplicationStatus.ACCEPTED,
    )

    application.status = s.BaseApplication.ApplicationStatus.PENDING
    db.commit()

    response = client.put(
        f"api/application/{application.uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )

    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(application)
    assert application.status == s.BaseApplication.ApplicationStatus.ACCEPTED

    job = db.scalar(select(m.Job).where(m.Job.id == application.job_id))
    assert job.worker_id == application.worker_id
    applications = db.scalars(
        select(m.Application).where((m.Application.job_id == application.job_id))
    ).all()

    # check for payment commission for both of users
    assert db.scalar(
        select(m.PlatformComission).where(
            m.PlatformComission.user_id == request_data.owner_id,
            m.PlatformComission.job_id == request_data.job_id,
        )
    )
    assert db.scalar(
        select(m.PlatformComission).where(
            m.PlatformComission.user_id == request_data.worker_id,
            m.PlatformComission.job_id == request_data.job_id,
        )
    )
    assert db.scalar(
        select(m.Notification).where(
            and_(
                m.Notification.entity_id == application.id,
                m.Notification.type == s.NotificationType.APPLICATION_ACCEPTED,
            )
        )
    )

    for exist_application in applications:
        if exist_application.id != application.id:
            assert (
                exist_application.status == s.BaseApplication.ApplicationStatus.DECLINED
            )


# TODO test create coule platform payments and then check
