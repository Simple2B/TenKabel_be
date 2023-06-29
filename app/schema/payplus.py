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
