from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
    has_payplus_car_uid: bool
    card_name: str
    is_payment_method_invalid: bool
