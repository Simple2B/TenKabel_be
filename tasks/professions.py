import json

from invoke import task
from sqlalchemy import select

from app.logger import log
from app.database import db as dbo
import app.model as m


@task
def initialize_professions(_):
    # opening json file with professions
    db = dbo.Session()
    with open("app/assets/json/professions.json") as f:
        professions = json.load(f)
        new_items = 0
        for key, value in professions.items():
            profession: m.Profession | None = db.scalars(
                select(m.Profession).where(m.Profession.name_en.ilike(f"%{key}%"))
            ).first()
            if not profession:
                new_items += 1
                profession = m.Profession(
                    name_en=key,
                    name_hebrew=value,
                )
                db.add(profession)
                db.commit()
        log(log.INFO, "%s new professions added", new_items)
