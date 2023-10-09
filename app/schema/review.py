from pydantic import BaseModel, validator

from .tag import TagIn, TagOut


class BaseReview(BaseModel):
    job_uuid: str
    evaluated_id: int
    evaluates_id: int

    class Config:
        use_enum_values = True
        orm_mode = True


class ReviewIn(BaseReview):
    rates: list[TagIn]

    @validator("rates")
    def check_rates(cls, v):
        rate = [tag.rate for tag in v]
        if len(rate) != len(set(rate)):
            raise ValueError("rate must be unique")
        return v


class ReviewOut(BaseReview):
    tag: TagOut

    class Config:
        use_enum_values = True
        orm_mode = True


class ReviewsOut(BaseReview):
    tags: list[TagOut] | None
