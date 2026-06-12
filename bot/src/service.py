from sqlalchemy import select, update
from sqlalchemy.orm import Session

from datetime import datetime
from uuid import uuid4

from .wrappers import with_session
from .models import Group, Admin, User, Template, Job
from .enums import StatusesEn, TemplateNames


@with_session
def get_groups(session: Session | None = None) -> list:
    stmt = select(Group.group_id, Group.token)
    return session.scalars(stmt).all()

@with_session
def get_admins(group_id: int, session: Session | None = None) -> list[int]:
    stmt = select(Admin.user_id).where(Admin.group_id == group_id)
    return session.scalars(stmt).all()

@with_session
def user_in_db(group_id: int, user_id: int, session: Session | None = None) -> bool:
    stmt = select(User.user_id).where(User.user_id == user_id, User.group_id == group_id)
    return True if session.scalars(stmt).one_or_none else False

@with_session
def add_user(group_id: int, user_info: dict, session: Session | None = None) -> None:
    new_user = User(
        group_id = group_id,
        user_id = user_info['user_id'],
        first_name = user_info['first_name'],
        last_name = user_info['last_name']
    )

    session.add(new_user)

@with_session
def get_template(group_id: int, session: Session | None = None) -> Template:
    stmt = select(Template).where(Template.group_id == group_id)

    return session.scalars(stmt).one_or_none()

@with_session
def get_number_users(group_id: int, session: Session | None = None) -> int:
    return len(session.scalars(select(User).where(User.group_id == group_id)).all())

@with_session
def add_job(group_id: int, datetime: datetime, user_id: int, session: Session | None = None) -> str:
    uuid_job = uuid4().__str__()

    new_job = Job(
        uuid=uuid_job,
        owner_id=user_id,
        group_id=group_id,
        run_at=datetime,
        status=StatusesEn.PENDING
    )
    
    session.add(new_job)
    return uuid_job

@with_session
def update_template(group_id: int, field: str, text: str, session: Session | None = None) -> None:
    if field == TemplateNames.SUBSCRIBE:
        stmt = update(Template).where(Template.group_id == group_id).values(subscribed=text)
    elif field == TemplateNames.NOT_SUBSCRIBE:
        stmt = update(Template).where(Template.group_id == group_id).values(not_subscribed=text)
    else:
        stmt = update(Template).where(Template.group_id == group_id).values(distribution=text)
    
    session.execute(stmt)