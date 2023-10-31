from invoke import task
from sqlalchemy.exc import IntegrityError

from app.config import get_settings, Settings
from app.logger import log
from app.database import db as dbo
import app.model as m


@task
def create_superuser(_):
    db = dbo.Session()
    settings: Settings = get_settings()
    superuser: m.SuperUser | None = db.query(m.SuperUser).first()
    if not superuser:
        superuser = m.SuperUser(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            password=settings.ADMIN_PASSWORD,
        )
        db.add(superuser)
        try:
            db.commit()
            log(log.INFO, "Superuser created")
        except IntegrityError as e:
            log(log.ERROR, "Error while creating user:\n%s", e)
    else:
        log(log.INFO, "Superuser already exists")
