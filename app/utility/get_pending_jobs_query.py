from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app import schema as s
from app import model as m


def get_pending_jobs_query_for_user(db: Session, user: m.User):
    query = select(m.Job).where(
        and_(
            m.Job.is_deleted == False,  # noqa E712
            m.Job.status == s.enums.JobStatus.PENDING,
        )
    )
    if user:
        applications_ids = db.scalars(
            select(m.Application.id).where(m.Application.worker_id == user.id)
        ).all()
        query = query.where(
            and_(m.Job.owner_id != user.id, m.Job.id.notin_(applications_ids))
        )

    return query
