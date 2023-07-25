from pydantic import BaseModel
from app.config import get_settings

settings = get_settings()


class Token(BaseModel):
    mobile_app_version: str = settings.MINIMUM_MOBILE_APP_VERSION
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: str = None
