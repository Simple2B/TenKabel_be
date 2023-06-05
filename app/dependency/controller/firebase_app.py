import firebase_admin
from firebase_admin import credentials

from app.config import get_settings, Settings

settings = get_settings()


def initialize_firebase_app(settings: Settings) -> None:
    firebase_cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(firebase_cred)
