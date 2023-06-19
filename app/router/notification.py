from fastapi import Depends, APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependency import get_current_user
import app.model as m
import app.schema as s
from app.logger import log
from app.database import get_db


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
