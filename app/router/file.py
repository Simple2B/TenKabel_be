from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.controller import AttachmentController
from app.database import get_db
from app.logger import log
from app.dependency import get_google_storage_client, get_file_by_uuid, get_current_user
from app.config import get_settings, Settings
import app.schema as s
import app.model as m

file_router = APIRouter(prefix="/files", tags=["Files"])


@file_router.get(
    "/{file_uuid}",
    response_model=s.FileOut,
    status_code=status.HTTP_200_OK,
)
def get_file(
    file_uuid: str,
    db: Session = Depends(get_db),
    file: m.File = Depends(get_file_by_uuid),
):
    return file


@file_router.post(
    "",
    response_model=s.FileOut,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: m.User = Depends(get_current_user),
    google_storage_client=Depends(get_google_storage_client),
    settings: Settings = Depends(get_settings),
):
    # uploading file to google cloud bucket
    if not file:
        log(log.INFO, "File not found")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File not found",
        )

    destination_blob_name = f"attachments/{current_user.uuid}/{file.filename}"
    blob = AttachmentController.upload_file_to_google_cloud_storage(
        filename=file.filename,
        file=file,
        destination_filename=destination_blob_name,
        google_storage_client=google_storage_client,
        settings=settings,
    )
    user_file = db.scalar(
        select(m.File).where(
            and_(
                m.File.url == blob.public_url,
                m.File.user_id == current_user.id,
            )
        )
    )
    if not user_file:
        # creating file in database
        new_file = m.File(
            user_id=current_user.id,
            original_filename=file.filename,
            url=blob.public_url,
        )
        log(log.INFO, "File %s uploaded", new_file)
        db.add(new_file)
        try:
            db.commit()
            db.refresh(new_file)
        except SQLAlchemyError as e:
            log(log.ERROR, "File %s failed to upload - %s", new_file, e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Failed to upload file",
            )
        return new_file
    else:
        log(log.INFO, "File %s already exists", user_file)
    return user_file


@file_router.delete("/{file_uuid}", status_code=status.HTTP_200_OK)
def delete_file(
    file_uuid: str,
    db: Session = Depends(get_db),
    google_storage_client=Depends(get_google_storage_client),
    settings: Settings = Depends(get_settings),
    file: m.File = Depends(get_file_by_uuid),
):
    # deleting from bucket
    AttachmentController.delete_file_from_google_cloud_storage(
        filename=file.storage_path,
        google_storage_client=google_storage_client,
        settings=settings,
    )
    db.delete(file)
    try:
        db.commit()
    except SQLAlchemyError as e:
        log(
            log.INFO,
            "Error while deleting file - [%s]:\n%s",
            file.uuid,
            e,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error while deleting file",
        )
    log(log.INFO, "File %s deleted", file)
    return status.HTTP_200_OK
