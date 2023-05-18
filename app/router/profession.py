from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s

from app.database import get_db

profession_router = APIRouter(prefix="/profession", tags=["Jobs"])


@profession_router.get(
    "/professions", status_code=status.HTTP_200_OK, response_model=s.ProfessionList
)
def get_professions(db: Session = Depends(get_db)):
    professions: list[m.Profession] = db.scalars(
        select(m.Profession).order_by(m.Profession.id)
    ).all()
    return s.ProfessionList(professions=professions)