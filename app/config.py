from functools import lru_cache

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URI: str
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@admin.com"
    DEFAULT_PAGE_SIZE: int = 100

    # GOOGLE
    GOOGLE_BUCKET_NAME: str = "tenkabel"
    GOOGLE_SERVICE_ACCOUNT_PATH: str = "./google_cloud_service_account.json"

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "./firebase_service_account.json"

    class Config:
        env_file = "project.env", ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
