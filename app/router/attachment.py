import base64
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.controller import AttachmentController
from app.dependency import get_current_user, get_current_attachment
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
def upload_attachment(
    attachment: s.AttachmentIn,
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    google_storage_client=Depends(get_google_storage_client),
    settings: Settings = Depends(get_settings),
):
    # uploading file to google cloud bucket
    decoded_file = base64.b64decode(attachment.file)
    filename = f"{int(datetime.now().timestamp())}_{attachment.filename}"
    destination_blob_name = f"attachments/{current_user.uuid}/{attachment.filename}"
    extension = attachment.filename.split(".")[-1]
    blob = AttachmentController.upload_file_to_google_cloud_storage(
        decoded_file=decoded_file,
        filename=attachment.filename,
        destination_filename=destination_blob_name,
        google_storage_client=google_storage_client,
        settings=settings,
    )
    # storing data to DB
    attachment = m.Attachment(
        storage_path=destination_blob_name,
        original_filename=attachment.filename,
        filename=filename,
        extension=extension,
        type=AttachmentController.get_type_by_extension(extension),
        url=blob.public_url,
        created_by_id=current_user.id,
    )
    db.add(attachment)
    try:
        db.commit()
        db.refresh(attachment)
    except SQLAlchemyError as e:
        log.error(e)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error while saving image",
        )
    return attachment


@attachment_router.delete("/{attachment_uuid}", status_code=status.HTTP_200_OK)
def delete_attachment(
    attachment_uuid: str,
    db: Session = Depends(get_db),
    google_storage_client=Depends(get_google_storage_client),
    settings: Settings = Depends(get_settings),
    attachment: m.Attachment = Depends(get_current_attachment),
):
    # deleting from bucket
    AttachmentController.delete_file_from_google_cloud_storage(
        filename=attachment.storage_path,
        google_storage_client=google_storage_client,
        settings=settings,
    )
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
