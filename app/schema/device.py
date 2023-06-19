from pydantic import BaseModel


class DeviceIn(BaseModel):
    uuid: str
    push_token: str


class DeviceOut(DeviceIn):
    id: int
    user_id: int
