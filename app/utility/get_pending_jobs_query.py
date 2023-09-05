from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app import schema as s
from app import model as m


def get_pending_jobs_query_for_user(db: Session, user: m.User):
    query = select(m.Job).where(
        and_(
            m.Job.is_deleted.is_(False),
            m.Job.status == s.enums.JobStatus.PENDING,
        )
    )
    if user:
        query = query.where(
            and_(
                m.Job.owner_id != user.id,
                m.User.applications.any(m.Application.job_id == m.Job.id),
            )
        )

    return query
