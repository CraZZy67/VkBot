from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from redis import Redis

from .constants import (
    POSTGRES_DRIVER,
    POSTGRES_HOST_NAME,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SYSTEM,
    POSTGRES_USER,
    REDIS_HOST_NAME,
    REDIS_PORT,
    LOG_LEVEL
)
from .c_logger import LogLevelsEn


class Base(DeclarativeBase): 
    pass

connect_string = f'{POSTGRES_SYSTEM}+{POSTGRES_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}'

if LOG_LEVEL == LogLevelsEn.debug.value:
    engine = create_engine(connect_string, echo=True)
else:
    engine = create_engine(connect_string)

Session = sessionmaker(bind=engine)

redis = Redis(
    host=REDIS_HOST_NAME,
    port=REDIS_PORT,
    decode_responses=True
)

feedback_text = 'Рассылка запланированая на дату: \n({date}) была разослана. \nУдалено пользователей из БД: {count}'
error_feedback_text = 'Рассылка запланированая на дату \n({date}), завершилась ошибкой'