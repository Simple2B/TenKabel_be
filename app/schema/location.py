from pydantic import BaseModel


class BaseLocation(BaseModel):
    name: str


class Location(BaseLocation):
    id: int
    uuid: str
