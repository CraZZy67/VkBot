from sqlalchemy import select
from sqlalchemy.orm import Session

from .wrappers import with_session
from .models import Group, Job


@with_session
def get_groups(session: Session | None = None) -> list[tuple]:
    stmt = select(Group.group_id)
    return session.execute(stmt).all()

@with_session
def get_jobs(group_id: int, session: Session | None = None) -> list[tuple]:
    stmt = select(Job.owner_id, Job.uuid, Job.run_at).where(Job.group_id == group_id)
    return session.execute(stmt).all()