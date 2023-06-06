from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
