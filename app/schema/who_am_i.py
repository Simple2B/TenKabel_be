from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
    is_payplus_card_uid: bool
