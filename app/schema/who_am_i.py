from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
    payplus_card_uid: str | None
