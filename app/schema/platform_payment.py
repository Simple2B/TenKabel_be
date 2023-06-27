from pydantic import BaseModel, AnyHttpUrl

from .enums import PlatformPaymentStatus


class PlatformPaymentLinkOut(BaseModel):
    url: AnyHttpUrl


class PlatformPaymentLinkIn(BaseModel):
    payment_page_uid: str
    charge_method: int = 1
    amount: int
    currency_code: str = "USD"  # ILS
    refURL_success: str | None
    refURL_failure: str | None
    refURL_cancel: str | None
    refURL_callback: str | None
    create_token: bool = True
    more_info_1: str


class PlatformPayment(BaseModel):
    uuid: str
    status: PlatformPaymentStatus

    class Config:
        orm_mode = True
