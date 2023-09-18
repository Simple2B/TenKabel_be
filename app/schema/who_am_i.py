from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
    has_payplus_card_uid: bool
    card_name: str
    is_payment_method_invalid: bool
    is_auth_by_google: bool
    is_auth_by_apple: bool
