from pydantic import BaseModel

from .user import User


class PlatformCommission(BaseModel):
    uuid: str
    user_id: int
    user: User
    job_id: int
    platform_payment_id: int

    class Config:
        orm_mode = True
