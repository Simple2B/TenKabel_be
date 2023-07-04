from functools import lru_cache
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URI: str
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@admin.com"
    DEFAULT_PAGE_SIZE: int = 10

    # PayPlus
    PAY_PLUS_API_KEY: str = ""
    PAY_PLUS_SECRET_KEY: str = ""
    PAY_PLUS_API_URL: str = ""
    PAY_PLUS_TERMINAL_ID: str = ""
    PAY_PLUS_CASHIERS_ID: str = ""
    PAY_PLUS_PAYMENT_PAGE_ID: str = ""
    PAYPLUS_CURRENCY_CODE: str = "ILS"

    # GOOGLE
    GOOGLE_BUCKET_NAME: str = "tenkabel"
    GOOGLE_SERVICE_ACCOUNT_PATH: str = ""

    # REDIS
    REDIS_URL: str = "redis://:password@redis"
    FEE_PAY_DAY: int = 3
    DAILY_REPORT_HOURS: int = 22
    DAILY_REPORT_MINUTES: int = 0

    VAT_COEFFICIENT: float = 1.17
    COMISSION_COEFFICIENT: float = 0.009

    class Config:
        env_file = "project.env", ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
