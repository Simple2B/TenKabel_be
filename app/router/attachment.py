import base64

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from app.dependency import get_current_user
from app.database import get_db
import app.model as m
import app.schema as s

from app.logger import log
from app.dependency import get_google_storage_client
from app.config import get_settings, Settings

attachment_router = APIRouter(prefix="/attachments", tags=["Attachments"])


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
    def get_type_by_extension(extension: str) -> s.enums.AttachmentType:
        if extension in ["jpg", "jpeg", "png", "png", "gif", "svg", "webp", "tiff"]:
            return s.enums.AttachmentType.IMAGE
        elif extension in ["pdf", "doc", "docx"]:
            return s.enums.AttachmentType.DOCUMENT

    def upload_file_to_google_cloud_storage(destination_filename: str):
        bucket = google_storage_client.get_bucket(settings.GOOGLE_STORAGE_BUCKET_NAME)

        blob = bucket.blob(attachment.filename)
        blob = bucket.blob(destination_filename)
        blob.upload_from_string(decoded_file)
        return blob

    # uploading file to google cloud bucket
    decoded_file = base64.b64decode(attachment.file)
    destination_blob_name = f"attachments/{current_user.uuid}/{attachment.filename}"
    extension = attachment.filename.split(".")[-1]
    blob = upload_file_to_google_cloud_storage(
        destination_filename=destination_blob_name
    )
    # storing data to DB
    attachment = m.Attachment(
        original_filename=destination_blob_name,
        filename=attachment.filename,
        extension=extension,
        type=get_type_by_extension(extension),
        url=blob.public_url,
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
