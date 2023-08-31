from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db


options_router = APIRouter(prefix="/options", tags=["Options"])


@options_router.get(
    "/price", status_code=status.HTTP_200_OK, response_model=s.PriceOption
)
def get_max_min_price(
    db: Session = Depends(get_db),
):
    price_query = select(
        func.max(m.Job.payment).label("max_price"),
        func.min(m.Job.payment).label("min_price"),
    ).where(m.Job.is_deleted.is_(False))

    result = db.execute(price_query).first()
    log(
        log.INFO,
        "Max price is - %s, min price is - %s",
        result.max_price,
        result.min_price,
    )
    return s.PriceOption(max_price=result.max_price, min_price=result.min_price)
