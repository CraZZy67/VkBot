from sqlalchemy import select
from sqlalchemy.orm import Session

from .wrappers import with_session
from .models import Group


@with_session
def get_groups(session: Session | None = None) -> list:
    stmt = select(Group.group_id, Group.token)
    return session.scalars(stmt).all()