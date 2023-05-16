from pydantic import BaseModel


class BaseProfession(BaseModel):
    name_en: str
    name_hebrew: str

    class Config:
        orm_mode = True


class Profession(BaseProfession):
    id: int
    uuid: str

    class Config:
        orm_mode = True


class ProfessionList(BaseModel):
    professions: list[Profession]
