import enum

from pydantic import BaseModel


class Rate(BaseModel):
    class RateStatus(enum.Enum):
        POSITIVE = "positive"
        NEGATIVE = "negative"
        NEUTRAL = "neutral"

    id: int
    uuid: str
    rate: RateStatus | str

    class Config:
        use_enum_values = True
        orm_mode = True


class RateList(BaseModel):
    rates: list[Rate]
