from fastapi import HTTPException, status
from google.cloud.exceptions import GoogleCloudError
from google.cloud import storage
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app import model as m
from app import schema as s
from app.logger import log
from app.config import Settings
from app.dependency.file import get_current_file


class AttachmentController:
    @staticmethod
    def get_type_by_extension(extension: str) -> s.enums.AttachmentType:
        if extension in [e.value for e in s.enums.ImageExtension]:
            return s.enums.AttachmentType.IMAGE
        return s.enums.AttachmentType.DOCUMENT

    @staticmethod
    def upload_file_to_google_cloud_storage(
        decoded_file: bytes,
        filename: str,
        destination_filename: str,
        google_storage_client,
        settings: Settings,
    ) -> storage.Blob:
        bucket = google_storage_client.get_bucket(settings.GOOGLE_STORAGE_BUCKET_NAME)

        blob = bucket.blob(filename)
        blob = bucket.blob(destination_filename)
        try:
            blob.upload_from_string(decoded_file)
        except GoogleCloudError as e:
            log(log.INFO, "Error while uploading file to google cloud storage:\n%s", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while uploading file to google cloud storage",
            )

        return blob

    @staticmethod
    def validate_files(
        file_uuids: list[str], user: m.User, db: Session
    ) -> list[m.File]:
        files = []
        for file_uuid in file_uuids:
            file: m.File = get_current_file(file_uuid, user=user, db=db)
            files.append(file)

        return files

    @staticmethod
    def create_attachments(
        current_user: m.User, request_data: s.AttachmentIn, db: Session
    ):
        files: list[s.Attachment] = AttachmentController.validate_files(
            request_data.file_uuids, current_user, db
        )
        job = db.scalars(select(m.Job).where(m.Job.id == request_data.job_id)).first()
        if not job:
            log(log.INFO, "Job %s not found", request_data.job_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )
        if current_user.id != job.owner_id and current_user.id != job.worker_id:
            log(
                log.INFO, "User %s is not allowed to create attachment", current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not allowed to create attachment to this job",
            )

        for file in files:
            attachment = m.Attachment(
                user_id=current_user.id,
                job_id=request_data.job_id,
                file_id=file.id,
            )
            db.add(attachment)

        try:
            db.commit()
        except SQLAlchemyError as e:
            log.error(e)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while saving attachment",
            )
        return attachment

    @staticmethod
    def delete_file_from_google_cloud_storage(
        filename: str,
        google_storage_client,
        settings: Settings,
    ):
        bucket = google_storage_client.get_bucket(settings.GOOGLE_STORAGE_BUCKET_NAME)
        blob = bucket.blob(filename)
        try:
            blob.delete()
        except GoogleCloudError as e:
            log(log.INFO, "Error while deleting file from google cloud storage:\n%s", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error while deleting file from google cloud storage",
            )
        log(log.INFO, "Deleting file %s from google cloud client", filename)
