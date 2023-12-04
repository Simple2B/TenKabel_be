from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s

from app.logger import log
from app.database import get_db

profession_router = APIRouter(prefix="/professions", tags=["Jobs"])


@profession_router.get(
    "", status_code=status.HTTP_200_OK, response_model=s.ProfessionList
)
def get_professions(db: Session = Depends(get_db)):
    professions: list[m.Profession] = db.scalars(
        select(m.Profession)
        .where(m.Profession.is_deleted == False)  # noqa E712
        .order_by(m.Profession.id)
    ).all()
    log(log.INFO, "Professions list (%s) returned", len(professions))
    return s.ProfessionList(professions=professions)
