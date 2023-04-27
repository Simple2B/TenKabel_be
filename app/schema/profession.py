from pydantic import BaseModel


class BaseProfession(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Profession(BaseProfession):
    id: int
    uuid: str

    class Config:
        orm_mode = True
