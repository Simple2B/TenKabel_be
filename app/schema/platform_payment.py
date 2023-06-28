from pydantic import BaseModel, AnyHttpUrl, validator

from .enums import PlatformPaymentStatus


class PlatformPaymentLinkOut(BaseModel):
    url: AnyHttpUrl


class PlatformPaymentLinkIn(BaseModel):
    payment_page_uid: str
    charge_method: int = 1
    amount: float
    currency_code: str = "USD"  # ILS
    refURL_success: str | None
    refURL_failure: str | None
    refURL_cancel: str | None
    refURL_callback: str | None
    create_token: bool = True
    more_info_1: str

    @validator("amount")
    def round_amount(cls, v):
        return round(v, 2)


class PlatformPayment(BaseModel):
    uuid: str
    status: PlatformPaymentStatus

    class Config:
        orm_mode = True
