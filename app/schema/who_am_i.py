from pydantic import BaseModel


class WhoAmIOut(BaseModel):
    uuid: str
    has_payplus_car_uid: bool
