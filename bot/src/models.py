from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .config import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer(), unique=True)
    token: Mapped[str] = mapped_column(String(), unique=True)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]

class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    subscribed: Mapped[str]
    not_subscribed: Mapped[str]
    distribution: Mapped[str]