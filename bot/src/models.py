from sqlalchemy import Integer, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from .config import Base
from .enums import JobStatusesEn


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer(), unique=True)
    token: Mapped[str] = mapped_column(String(), unique=True)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str]
    last_name: Mapped[str]

class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'), unique=True)
    subscribed: Mapped[str] = mapped_column(default='Default text sub')
    not_subscribed: Mapped[str] = mapped_column(default='Default text un_sub')
    distribution: Mapped[str] = mapped_column(default='Default text dist')

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id: Mapped[int]

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    owner_id: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    run_at: Mapped[datetime]
    status: Mapped[JobStatusesEn] = mapped_column(ENUM(JobStatusesEn, name='job_statuses', create_type=True))