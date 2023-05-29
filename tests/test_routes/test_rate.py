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
)


def test_rate_methods(client: TestClient, db: Session, test_data: TestData):
    request_data = s.BaseRate(
        rate=test_data.test_rate.rate,
        giver_id=int(test_data.test_rate.giver_id),
        user_id=int(test_data.test_rate.user_id),
    )
    user: m.User = db.scalar(select(m.User).where(m.User.id == request_data.user_id))
    count_rates_before = user.positive_rates_count

    response = client.post("api/rate", data=request_data.json())
    assert response.status_code == status.HTTP_201_CREATED

    assert user.positive_rates_count == count_rates_before + 1
    rate: m.Rate = db.scalar(
        select(m.Rate).where(
            m.Rate.rate == s.BaseRate.RateStatus(test_data.test_rate.rate)
            and m.User.giver_id == int(test_data.test_rate.giver_id)
            and m.User.user_id == int(test_data.test_rate.user_id)
        )
    )
    assert rate.giver_id == int(
        test_data.test_rate.giver_id
    ) and rate.rate == s.BaseRate.RateStatus(test_data.test_rate.rate)

    request_data = s.BaseRate(
        rate=s.BaseRate.RateStatus.NEGATIVE,
        giver_id=int(test_data.test_rate.giver_id),
        user_id=int(test_data.test_rate.user_id),
    )

    response = client.put(f"api/rate/{rate.uuid}", data=request_data.json())
    assert response.status_code == status.HTTP_200_OK
    db.refresh(rate)
    assert rate.rate == s.BaseRate.RateStatus(request_data.rate)

    fill_test_data(db)
    create_professions(db)

    rate: m.Rate = db.scalar(select(m.Rate))
    response = client.get(f"api/rate/{rate.uuid}")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.Rate.parse_obj(response.json())
    assert resp_obj.id == rate.id
