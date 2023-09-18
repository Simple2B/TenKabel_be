from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select, func, or_
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
    min_selected: int = None,
    max_selected: int = None,
    regions: Annotated[list[str] | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
):
    price_query = select(
        func.max(m.Job.payment).label("max_price"),
        func.min(m.Job.payment).label("min_price"),
    ).where(m.Job.is_deleted.is_(False))
    filters = []
    if regions:
        for region in regions:
            filters.append(m.Job.regions.any(m.Location.name_en == region))

    if category:
        category = db.scalars(
            select(m.Profession).where(m.Profession.name_en == category)
        ).first()
        filters.append(m.Job.profession_id == category.id)

    price_query = price_query.where(or_(*filters))
    result = db.execute(price_query).first()
    log(
        log.INFO,
        "Max price is - %s, min price is - %s, region is - %s",
        result.max_price,
        result.min_price,
        regions,
    )
    # if min_selected and min_selected > result.min_price:
    #     result.min_price = min_selected
    # if max_selected and max_selected < result.max_price:
    #     result.max_price = max_selected

    return s.PriceOption(
        max_price=result.max_price,
        min_price=result.min_price,
    )
