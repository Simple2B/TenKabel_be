from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.controller import AttachmentController
from app.dependency import (
    get_current_user,
    get_current_attachment,
)
from app.database import get_db
import app.model as m
import app.schema as s

from app.logger import log
from app.dependency import get_google_storage_client
from app.config import get_settings, Settings

attachment_router = APIRouter(prefix="/attachments", tags=["Attachments"])


@attachment_router.get(
    "/{attachment_uuid}",
    response_model=s.AttachmentOut,
    status_code=status.HTTP_200_OK,
)
def get_attachment(
    attachment_uuid: str,
    db: Session = Depends(get_db),
    attachment: m.Attachment = Depends(get_current_attachment),
):
    # code repeated from get_current_attachment, isn't it?
    attachment: m.Attachment = db.scalars(
        select(m.Attachment).where(m.Attachment.uuid == attachment_uuid)
    ).first()
    if not attachment:
        log(log.INFO, "Attachment %s not found", attachment_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    return attachment


@attachment_router.post(
    "",
    response_model=s.AttachmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_attachment(
    request_data: s.AttachmentIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    return AttachmentController.create_attachments(
        current_user=current_user,
        request_data=request_data,
        db=db,
    )


@attachment_router.delete("/{attachment_uuid}", status_code=status.HTTP_200_OK)
def delete_attachment(
    attachment_uuid: str,
    db: Session = Depends(get_db),
    google_storage_client=Depends(get_google_storage_client),
    settings: Settings = Depends(get_settings),
    attachment: m.Attachment = Depends(get_current_attachment),
):
    # deleting from bucket
    attachment.is_deleted = True
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(
            log.INFO,
            "Error while deleting attachment - [%s]:\n%s",
            attachment.uuid,
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error while deleting attachment",
        )

    return status.HTTP_200_OK
