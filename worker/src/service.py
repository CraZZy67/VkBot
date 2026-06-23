from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from datetime import datetime

from .wrappers import with_session
from .models import User, Template, Group, Job
from .constants import WORKER_YIELD_PER
from .enums import JobStatusesEn


@with_session
def get_users(group_id: int, session: Session | None = None) -> list[User]:
    stmt = select(User).where(User.group_id == group_id)
    stmt.execution_options(yield_per=WORKER_YIELD_PER)

    return session.scalars(stmt)

@with_session
def get_template(group_id: int, session: Session | None = None) -> str:
    stmt = select(Template.distribution).where(Template.group_id == group_id)
    return session.execute(stmt).one()[0]

@with_session
def get_group_token(group_id: int, session: Session | None = None) -> str:
    stmt = select(Group.token).where(Group.group_id == group_id)
    return session.execute(stmt).one()[0]

@with_session
def del_users(group_id: int, users: list, session: Session | None = None) -> None:
    stmt = delete(User).where(User.group_id == group_id, User.user_id.in_(users))
    session.execute(stmt)

@with_session
def get_job_info(uuid: str, session: Session | None = None) -> list[int, datetime]:
    stmt = select(Job.owner_id, Job.run_at).where(Job.uuid == uuid)
    return session.execute(stmt).one()

@with_session
def update_status(uuid: str, status: JobStatusesEn, session: Session | None = None) -> None:
    stmt = update(Job).where(Job.uuid == uuid).values(status=status)
    session.execute(stmt)