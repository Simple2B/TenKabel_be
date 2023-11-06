from pydantic import BaseModel


class PriceOption(BaseModel):
    max_price: float | None
    min_price: float | None
