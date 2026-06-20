from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from .wrappers import with_session
from .models import Group, Job
from .enums import JobStatusesEn


@with_session
def get_groups(session: Session | None = None) -> list[tuple]:
    stmt = select(Group.group_id)
    return session.execute(stmt).all()

@with_session
def get_jobs(group_id: int, session: Session | None = None) -> list[tuple]:
    stmt = select(Job.owner_id, Job.uuid, Job.run_at, Job.status).where(Job.group_id == group_id)
    return session.execute(stmt).all()

@with_session
def del_job(uuid: str, session: Session | None = None) -> None:
    stmt = delete(Job).where(Job.uuid == uuid)
    session.execute(stmt)

@with_session
def update_status(uuid: str, status: JobStatusesEn, session: Session | None = None) -> None:
    stmt = update(Job).where(Job.uuid == uuid).values(status=status)
    session.execute(stmt)