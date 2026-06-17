from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime

from .config import Base
from .enums import JobStatusesEn


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer(), unique=True)
    token: Mapped[str] = mapped_column(String(), unique=True)

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str]
    owner_id: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    run_at: Mapped[datetime]
    status: Mapped[JobStatusesEn] = mapped_column(ENUM(JobStatusesEn, name='job_statuses', create_type=True), nullable=False)