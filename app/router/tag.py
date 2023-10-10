from fastapi import Depends, APIRouter, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

import app.model as m
import app.schema as s
from app.database import get_db
from app.config import Settings, get_settings
from app.dependency import get_current_user

tag_router = APIRouter(prefix="/tags", tags=["Tags"])


@tag_router.get(
    "/popular-tags", status_code=status.HTTP_200_OK, response_model=list[s.TagOut]
)
def get_popular_tags(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    tags = db.scalars(
        select(m.Tag)
        .join(m.Review)
        .group_by(m.Review.tag_id)
        .order_by(func.count(m.Review.tag_id).desc())
        .limit(settings.POPULAR_TAGS_LIMIT)
    ).all()
    return tags


@tag_router.get("/", status_code=status.HTTP_200_OK, response_model=list[s.TagOut])
def get_user_tags(
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    tags = [review.tag for review in user.owned_rates]
    return tags
