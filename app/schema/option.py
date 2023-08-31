from pydantic import BaseModel


class PriceOption(BaseModel):
    max_price: float
    min_price: float
