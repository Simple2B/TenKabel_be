from app.config import Settings


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
    blob.upload_from_string(decoded_file)
    return blob
