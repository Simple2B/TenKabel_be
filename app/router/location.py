from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s

from app.logger import log
from app.database import get_db

location_router = APIRouter(prefix="/location", tags=["Location"])


@location_router.get(
    "/locations", status_code=status.HTTP_200_OK, response_model=s.LocationList
)
def get_locations(db: Session = Depends(get_db)):
    locations: list[m.Location] = db.scalars(
        select(m.Location).order_by(m.Location.id)
    ).all()
    log(log.INFO, "Locations list (%s) returned", len(locations))
    return s.LocationList(locations=locations)
