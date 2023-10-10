from pydantic import BaseModel
from .rate import BaseRate


class TagIn(BaseModel):
    rate: BaseRate.RateStatus
    tags: list[str]

    class Config:
        use_enum_values = True
        orm_mode = True


class TagOut(BaseModel):
    rate: BaseRate.RateStatus
    tag: str
    # profession_id: int | None

    class Config:
        use_enum_values = True
        orm_mode = True
