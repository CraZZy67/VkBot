from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .config import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str]
    last_name: Mapped[str]