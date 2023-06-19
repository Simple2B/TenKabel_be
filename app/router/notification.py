import re

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.dependency import get_current_user, get_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db
from app.utility import time_measurement
from app.utility.get_pending_jobs_query import get_pending_jobs_query_for_user


notification_router = APIRouter(prefix="/notification", tags=["Notifications"])


@notification_router.get(
    "/notifications", status_code=status.HTTP_200_OK, response_model=s.NotificationList
)
def get_notifications(
    db: Session = Depends(get_db), user: m.User = Depends(get_current_user)
):
    notifications: list[m.Notification] = db.scalars(
        select(m.Notification)
        .filter(m.Notification.user_id == user.id)
        .order_by(m.Notification.id.desc())
    ).all()

    log(log.INFO, "Notifications list (%s) returned", len(notifications))

    return s.NotificationList(
        items=[notification.create_schema(db) for notification in notifications]
    )
