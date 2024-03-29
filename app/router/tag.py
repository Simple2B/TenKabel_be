from fastapi import Depends, APIRouter, status, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.database import get_db
from app.config import Settings, get_settings
from app.dependency import get_current_user
from app.logger import log

tag_router = APIRouter(prefix="/tags", tags=["Tags"])


@tag_router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=s.ListTagOut,
)
def search_tags(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    q: str = Query(default="", trim_whitespace=True),
    count_of_rates: int = 3,  # len([_ for _ in s.BaseRate.RateStatus])
):
    query = select(m.Tag)
    if q:
        log(log.INFO, "search tag query is: - %s", q)
        query = query.where(m.Tag.tag.ilike(f"%{q}%"))
    tags = db.scalars(
        query.distinct().limit(settings.POPULAR_TAGS_LIMIT * count_of_rates)
    ).all()

    items = []
    for tag in tags:
        if len(items) >= settings.POPULAR_TAGS_LIMIT:
            break

        if tag.tag not in [item.tag for item in items]:
            items.append(tag)

    return s.ListTagOut(items=items)


@tag_router.get(
    "/popular-tags", status_code=status.HTTP_200_OK, response_model=list[s.TagOut]
)
def get_popular_tags(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    tags = db.scalars(
        select(m.Tag, func.count(m.Review.tag_id))
        .join(m.Review)
        .group_by(m.Tag.id)
        .order_by(func.count(m.Review.tag_id).desc())
        .limit(settings.POPULAR_TAGS_LIMIT)
    ).all()
    return tags


@tag_router.get("/", status_code=status.HTTP_200_OK, response_model=list[s.TagOut])
def get_user_tags(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
    user_uuid: str | None = None,
):
    if user_uuid:
        user = db.scalar(select(m.User).filter(m.User.uuid == user_uuid))
    if not user:
        log(log.INFO, "User wasn`t found [%s]", user_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    tags = [review.tag for review in user.given_rates]
    return tags
