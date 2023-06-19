from pydantic import BaseModel


class LogoutIn(BaseModel):
    device_uuid: str
