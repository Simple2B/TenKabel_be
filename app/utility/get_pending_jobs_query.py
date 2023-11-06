from sqlalchemy import select, and_
from sqlalchemy.orm import Session, aliased

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
        app_alias = aliased(m.Application)
        # Add a left outer join condition to check if there's a related application
        query = query.join(
            app_alias,
            onclause=and_(app_alias.job_id == m.Job.id, app_alias.owner_id == user.id),
            isouter=True,
        )

        query = query.where(
            and_(
                m.Job.owner_id != user.id,
                app_alias.id.is_(None),
            )
        )
    return query
