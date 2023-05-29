import enum

from pydantic import BaseModel


class BaseRate(BaseModel):
    class RateStatus(enum.Enum):
        POSITIVE = "positive"
        NEGATIVE = "negative"
        NEUTRAL = "neutral"

    giver_id: int
    user_id: int
    rate: RateStatus | str

    class Config:
        use_enum_values = True
        orm_mode = True


class Rate(BaseRate):
    id: int
    uuid: str

    class Config:
        use_enum_values = True
        orm_mode = True


class RateList(BaseModel):
    rates: list[Rate]
