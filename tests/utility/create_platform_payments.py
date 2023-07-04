from sqlalchemy.orm import Session

from app import model as m
from app import schema as s
from app.logger import log


def create_pending_platform_payment(db: Session, user: m.User, job: m.Job):
    db.add(
        m.PlatformCommission(
            user_id=user.id,
            job_id=job.id,
            status=s.enums.PlatformCommissionStatus.PENDING,
        )
    )
    db.commit()
    log(log.DEBUG, "PENDING Platform Payment for Job [%s] created", job.uuid)
