from datetime import datetime
from pydantic import BaseModel


class CardIn(BaseModel):
    credit_card_number: str
    card_date_mmyy: datetime
    card_name: str | None
