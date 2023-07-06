from pydantic import BaseModel


class PayplusCardIn(BaseModel):
    terminal_uid: str
    customer_uid: str
    credit_card_number: str
    card_date_mmyy: str


class PayplusCustomerIn(BaseModel):
    customer_name: str | None = None
    email: str
    phone: str | None = None


class PayplusToken(BaseModel):
    card_uid: str


class PayPlusCharge(BaseModel):
    terminal_uid: str
    cashier_uid: str
    amount: int
    currency_code: str | None
    use_token: bool = True
    token: str
    more_info_1: str | None
    credit_terms: int | None = 8
    customer_uid: str | None = None
