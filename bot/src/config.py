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

users_message_text = 'Пользователей в базе данных: {number}'
plane_message_text = 'Рассылка запланирована ⌚\n\nuuid: {uuid}\ndate: {month}.{day}/{minute}:{second}'
invalid_format_text = 'Не верный формат, попробуйте еще раз!'
file_change_text = 'Отправте файл на который вы хотите заменить текст.'
success_file_changed = 'Файл был успешно заменен!'

DATETIME_FORMAT = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\/(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$'

LOG_FORMAT = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"