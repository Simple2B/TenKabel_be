from app.config import Settings, get_settings

settings: Settings = get_settings()


def get_default_avatar() -> str:
    return settings.DEFAULT_AVATAR_PROFILE_URL
