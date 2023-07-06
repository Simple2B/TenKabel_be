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
    create_jobs_for_user,
    create_rates,
)


def test_rate_methods(
    client: TestClient,
    db: Session,
    test_data: TestData,
    authorized_users_tokens: list[s.Token],
):
    create_professions(db)
    fill_test_data(db)

    user: m.User = db.scalar(
        select(m.User).where(m.User.email == test_data.test_authorized_users[0].email)
    )
    create_jobs_for_user(db, user.id)
    create_rates(db)

    job: m.Job = db.scalar(
        select(m.Job).where(
            and_(
                m.Job.owner_id == user.id,
                m.Job.status == s.enums.JobStatus.JOB_IS_FINISHED,
            )
        )
    )
    if not job:
        job: m.Job = db.scalar(
            select(m.Job).where(
                and_(
                    m.Job.owner_id == user.id,
                    m.Job.status != s.enums.JobStatus.PENDING,
                )
            )
        )
        job.status = s.enums.JobStatus.JOB_IS_FINISHED
        db.commit()
    for rate in job.rates:
        db.delete(rate)
    db.commit()
    count_rates_before = user.positive_rates_count

    request_data = s.BaseRate(
        rate=test_data.test_rate.rate,
        owner_id=job.owner_id,
        worker_id=job.worker_id,
        job_id=job.id,
    )

    response = client.post(
        "api/rate",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {authorized_users_tokens[0].access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    assert user.positive_rates_count == count_rates_before + 1
    assert job.worker_rate_uuid is not None and job.owner_rate_uuid is None

    rate: m.Rate = db.scalar(
        select(m.Rate).where(
            and_(
                m.Rate.rate == s.BaseRate.RateStatus(request_data.rate),
                m.Rate.owner_id == request_data.owner_id,
                m.Rate.worker_id == request_data.worker_id,
            )
        )
    )
    assert rate.owner_id == job.owner_id and rate.rate == s.BaseRate.RateStatus(
        test_data.test_rate.rate
    )

    request_data = s.BaseRate(
        rate=s.BaseRate.RateStatus.NEGATIVE,
        owner_id=job.owner_id,
        worker_id=job.worker_id,
        job_id=job.id,
    )

    response = client.put(f"api/rate/{rate.uuid}", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(rate)
    assert rate.rate == s.BaseRate.RateStatus(request_data.rate)

    request_data = s.RatePatch(
        rate=s.BaseRate.RateStatus.POSITIVE,
    )

    response = client.patch(f"api/rate/{rate.uuid}", json=request_data.dict())
    assert response.status_code == status.HTTP_201_CREATED
    db.refresh(rate)
    assert rate.rate == s.BaseRate.RateStatus(request_data.rate)

    rate: m.Rate = db.scalar(select(m.Rate))
    response = client.get(f"api/rate/{rate.uuid}")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Rate.parse_obj(response.json())
    assert resp_obj.id == rate.id
