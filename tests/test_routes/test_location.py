from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.schema as s

from tests.utility import create_locations, fill_test_data, create_professions


def test_get_locations(client: TestClient, db: Session):
    # create users
    # create professions
    create_professions(db)
    create_locations(db)
    fill_test_data(db)
    response = client.get("api/location/locations")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.LocationList.parse_obj(response.json())
    assert len(resp_obj.locations) > 0
