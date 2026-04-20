from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from logger import LogLevelsEn
from .constants import (
    DB_DRIVER,
    DB_HOST_NAME,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_SYSTEM,
    DB_USER,
    LOG_LEVEL
)


class Base(DeclarativeBase): 
    pass

connect_string = f'{DB_SYSTEM}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST_NAME}:{DB_PORT}/{DB_NAME}'

if LOG_LEVEL == LogLevelsEn.debug.value:
    engine = create_engine(connect_string, echo=True)
else:
    engine = create_engine(connect_string)

Session = sessionmaker(bind=engine)