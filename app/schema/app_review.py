from datetime import datetime
from pydantic import BaseModel, Field


class AppReviewIn(BaseModel):
    stars_count: int = Field(None, ge=0, le=5)
    review: str = Field(..., max_length=1000)

    class Config:
        orm_mode = True
        use_enum_values = True


class AppReviewOut(AppReviewIn):
    id: int
    uuid: str
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True
