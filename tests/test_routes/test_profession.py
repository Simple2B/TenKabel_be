from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.utility import create_professions, fill_test_data

import app.schema as s


def test_get_professions(client: TestClient, db: Session):
    # create users
    fill_test_data(db)
    # create professions
    create_professions(db)

    response = client.get("api/profession/professions")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.ProfessionList.parse_obj(response.json())
    assert len(resp_obj.professions) > 0
