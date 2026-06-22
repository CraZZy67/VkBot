from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from datetime import datetime

from .config import Base
from .enums import JobStatusesEn


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str]
    owner_id: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    run_at: Mapped[datetime]
    status: Mapped[JobStatusesEn] = mapped_column(ENUM(JobStatusesEn, name='job_statuses', create_type=True), nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]