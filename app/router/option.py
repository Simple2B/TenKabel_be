from typing import Annotated

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select, func, or_, and_
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
    regions: Annotated[list[str] | None, Query()] = None,
    category: str | None = Query(default=None),
    user_uuid: str | None = Query(default=None),
):
    price_query = select(
        func.max(m.Job.payment).label("max_price"),
        func.min(m.Job.payment).label("min_price"),
    ).where(
        and_(
            m.Job.is_deleted.is_(False),
            m.Job.status == s.enums.JobStatus.PENDING,
        )
    )
    filters = []
    if regions:
        for region in regions:
            filters.append(m.Job.regions.any(m.Location.name_en == region))
        price_query = price_query.where(or_(*filters))

    if category:
        category = db.scalars(
            select(m.Profession).where(m.Profession.name_en == category)
        ).first()
        price_query = price_query.where(m.Job.profession_id == category.id)

    if user_uuid:
        user_id = db.scalars(select(m.User.id).where(m.User.uuid == user_uuid)).first()
        price_query = price_query.where(m.Job.owner_id != user_id)

    result = db.execute(price_query).first()
    log(
        log.INFO,
        "Max price is - %s min price is - %s regions are - %s category is - %s",
        result.max_price,
        result.min_price,
        regions,
        category.name_en if category else "None",
    )
    # handling extra logic when min price is greater than max price
    if result.min_price and result.max_price:
        if result.min_price > result.max_price:
            result.min_price, result.max_price = result.max_price, result.min_price

    return s.PriceOption(
        max_price=result.max_price,
        min_price=result.min_price,
    )
