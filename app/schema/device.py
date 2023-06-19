from pydantic import BaseModel
from .user import User


class DeviceIn(BaseModel):
    uuid: str
    push_token: str


class DeviceOut(DeviceIn):
    id: int
    user_id: int
