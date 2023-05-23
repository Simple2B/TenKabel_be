from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.utility import create_professions

import app.schema as s

from app.utility.create_test_users import fill_test_data
from app.utility import create_locations


def test_get_locations(client: TestClient, db: Session):
    # create users
    fill_test_data(db)
    # create professions
    create_professions(db)
    create_locations(db)
    response = client.get("api/location/locations")
    assert response.status_code == status.HTTP_200_OK
    resp_obj = s.LocationList.parse_obj(response.json())
    assert len(resp_obj.locations) > 0
