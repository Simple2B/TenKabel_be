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
    create_locations,
    create_jobs,
    create_jobs_for_user,
)


def test_review_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
    faker,
):
    fill_test_data(db)
    create_locations(db)
    create_professions(db)
    create_jobs(db)
    auth_user = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    create_jobs_for_user(db, auth_user.id)

    tags = ["test1", "test2"]
    job: m.Job = auth_user.jobs_owned[0]
    if not job.worker:
        job.worker_id = db.scalars(
            select(m.User.id).where(
                m.User.id != auth_user.id,
            )
        ).all()[10]

    job.set_enum(s.JobStatus.JOB_IS_FINISHED, db)
    db.commit()
    assert job.worker_id

    request_data: s.ReviewIn = s.ReviewIn(
        evaluated_id=job.worker.id,
        evaluates_id=job.owner.id,
        job_uuid=job.uuid,
        rates=[s.TagIn(rate=s.BaseRate.RateStatus.NEGATIVE, tags=tags)],
    )

    response = client.post(
        "api/reviews",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
        json=request_data.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert job.owner.negative_rates_count == len(tags)

    response = client.get(
        f"api/reviews/{job.reviews[0].uuid}",
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
