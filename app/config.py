from functools import lru_cache
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URI: str
    DEFAULT_PAGE_SIZE: int = 10
    DEFAULT_AVATAR_PROFILE_URL: (
        str
    ) = "https://storage.googleapis.com/tenkabel-stage/default_profile_image.png"
    # PayPlus
    PAY_PLUS_API_KEY: str = ""
    PAY_PLUS_SECRET_KEY: str = ""
    PAY_PLUS_API_URL: str = ""
    PAY_PLUS_TERMINAL_ID: str = ""
    PAY_PLUS_CASHIERS_ID: str = ""
    PAY_PLUS_PAYMENT_PAGE_ID: str = ""
    PAYPLUS_CURRENCY_CODE: str = "ILS"
    PAY_PLUS_DISABLED: bool = False

    # GOOGLE
    GOOGLE_STORAGE_BUCKET_NAME: str = "tenkabel-dev"
    GOOGLE_SERVICE_ACCOUNT_PATH: str = "./google_cloud_service_account.json"

    # REDIS
    REDIS_URL: str = "redis://:password@redis"
    FEE_PAY_DAY: int = 3
    DAILY_REPORT_HOURS: int = 22
    DAILY_REPORT_MINUTES: int = 0

    VAT_COEFFICIENT: float = 1.17
    COMMISSION_COEFFICIENT: float = 0.009

    POPULAR_TAGS_LIMIT: int = 5
    MINIMUM_MOBILE_APP_VERSION: str

    APP_STORE_LINK: str
    PLAY_MARKET_LINK: str

    ADMIN_USERNAME: str | None
    ADMIN_PASSWORD: str | None
    ADMIN_EMAIL: EmailStr | None

    NEW_USER_TERM_DAYS: int = 90

    class Config:
        env_file = "project.env", ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
