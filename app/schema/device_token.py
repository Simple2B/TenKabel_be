from pydantic import BaseModel


class BaseDeviceToken(BaseModel):
    token: str
