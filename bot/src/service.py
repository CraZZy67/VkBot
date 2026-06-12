from sqlalchemy import select
from sqlalchemy.orm import Session

from .wrappers import with_session
from .models import Group, Admin, User, Template


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

    session.add_all([new_user])

@with_session
def get_template(group_id: int, session: Session | None = None) -> Template:
    stmt = select(Template).where(Template.group_id == group_id)

    return session.scalars(stmt).one_or_none()