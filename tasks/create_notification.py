from invoke import task
from sqlalchemy import select, or_

from app import model as m
from app import schema as s
from app.logger import log

from datetime import datetime


@task
def create_notification_on_job_posting(_, user_credentials: str):
    from app.database import db as dbo

    db = dbo.Session()
    log(log.INFO, "user_credentials: " + user_credentials)
    try:
        user_id = int(user_credentials)
    except ValueError:
        user_id = None
    user: m.User = db.scalar(
        select(m.User).where(
            or_(
                m.User.email == user_credentials,
                m.User.phone == user_credentials,
                m.User.id == user_id,
            )
        )
    )

    if not user:
        raise Exception("User not found")

    if not (user.notification_locations_flag or user.notification_profession_flag):
        raise Exception("User has no notifications enabled")

    log(
        log.INFO,
        "HERE, [%s] - [%s]",
        user.notification_locations_flag,
        user.notification_profession_flag,
    )

    if user.notification_profession_flag:
        profession_id = (
            user.notification_profession[0].profession_id
            if user.notification_profession
            else user.professions[0].id
        )
        job_data: s.JobIn = s.JobIn(
            profession_id=profession_id,
            city=db.scalar(select(m.Location.name_en)),
            payment=10,
            commission=10,
            name="Test Task",
            description="Just do anything",
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer_first_name="test_first_name",
            customer_last_name="test_last_name",
            customer_phone="+3800000000",
            customer_street_address="test_location",
        )
        log(log.INFO, "Job created")
