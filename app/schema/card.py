from datetime import datetime
import re
from pydantic import BaseModel, validator


class CardIn(BaseModel):
    credit_card_number: str
    card_date_mmyy: datetime
    card_name: str | None = ""

    @validator("credit_card_number")
    def validate_credit_card_number(cls, value):
        cleaned_number = re.sub(r"\D", "", value)
        if not cleaned_number.isnumeric():
            raise ValueError("Invalid credit card number")
        if len(cleaned_number) < 13 or len(cleaned_number) > 16:
            raise ValueError("Invalid credit card number length")
        return cleaned_number
