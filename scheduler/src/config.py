from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from redis import Redis


from .constants import (
    POSTGRES_DRIVER,
    POSTGRES_HOST_NAME,
    POSTGRES_NAME,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SYSTEM,
    POSTGRES_USER,
    REDIS_HOST_NAME,
    REDIS_PASSWORD,
    REDIS_PORT,
    LOG_LEVEL
)
from .c_logger import LogLevelsEn


class Base(DeclarativeBase): 
    pass

connect_string = f'{POSTGRES_SYSTEM}+{POSTGRES_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_NAME}'

if LOG_LEVEL == LogLevelsEn.debug.value:
    engine = create_engine(connect_string, echo=True)
else:
    engine = create_engine(connect_string)

Session = sessionmaker(bind=engine)

redis = Redis(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)