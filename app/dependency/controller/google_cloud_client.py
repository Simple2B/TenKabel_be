from fastapi import Depends
from google.cloud import storage

from app.config import Settings, get_settings


def get_google_client(settings: Settings = Depends(get_settings)):
    client = storage.Client.from_service_account_json()
    return client
