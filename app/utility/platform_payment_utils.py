import json
import httpx

from app.logger import log
from app.config import get_settings, Settings

settings: Settings = get_settings()


def pay_plus_headers(settings: Settings):
    auth = {
        "api_key": settings.PAY_PLUS_API_KEY,
        "secret_key": settings.PAY_PLUS_SECRET_KEY,
    }
    auth = json.dumps(auth)
    return {
        "Content-Type": "application/json",
        "Authorization": auth,
    }
