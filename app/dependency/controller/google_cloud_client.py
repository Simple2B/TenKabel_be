from google.cloud import storage
from app.config import Settings, get_settings

settings: Settings = get_settings()


# Instantiates a client
def get_google_storage_client():
    return storage.Client.from_service_account_json(
        json_credentials_path=settings.GOOGLE_SERVICE_ACCOUNT_PATH
    )
