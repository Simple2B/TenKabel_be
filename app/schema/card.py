from datetime import datetime
from pydantic import BaseModel


class BaseCard(BaseModel):
    pass


class CardIn(BaseCard):
    card_name: str
    credit_card_number: str
    card_date_mmyy: datetime
    name: str | None


class CardOut(BaseCard):
    token: str
