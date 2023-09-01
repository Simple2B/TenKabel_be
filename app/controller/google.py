from fastapi import HTTPException, status
from google.cloud.exceptions import GoogleCloudError

from app.config import Settings
from app.logger import log


def upload_file_to_google_cloud_storage(
    decoded_file: bytes,
    filename: str,
    destination_filename: str,
    google_storage_client,
    settings: Settings,
):
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
