from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
import app.model as m
from app.logger import log

from .user import get_current_user


def get_current_attachment(
    attachment_uuid: str,
    user: m.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attachment: m.Attachment = db.scalars(
        select(m.Attachment).where(m.Attachment.uuid == attachment_uuid)
    ).first()
    if not attachment:
        log(log.INFO, "Attachment not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    if attachment.user.uuid != user.uuid:
        log(log.INFO, "Attachment %s not belongs to user %", attachment_uuid, user.uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    return attachment
