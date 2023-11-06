import enum

from pydantic import BaseModel


class BaseRate(BaseModel):
    # TODO: MIGRATE ENUM
    class RateStatus(enum.Enum):
        POSITIVE = "POSITIVE"
        NEGATIVE = "NEGATIVE"
        NEUTRAL = "NEUTRAL"

    job_id: int
    owner_id: int
    worker_id: int
    rate: RateStatus

    class Config:
        use_enum_values = True
        orm_mode = True


class RatePatch(BaseModel):
    job_id: int | None
    owner_id: int | None
    worker_id: int | None
    rate: BaseRate.RateStatus | None

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
