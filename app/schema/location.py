from pydantic import BaseModel


class BaseLocation(BaseModel):
    name_en: str
    name_hebrew: str


class Location(BaseLocation):
    id: int
    uuid: str

    class Config:
        orm_mode = True


class LocationList(BaseModel):
    locations: list[Location]
