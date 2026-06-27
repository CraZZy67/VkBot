from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .c_logger import LogLevelsEn
from .constants import (
    POSTGRES_DRIVER,
    POSTGRES_HOST_NAME,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SYSTEM,
    POSTGRES_USER,
    LOG_LEVEL
)


class Base(DeclarativeBase): 
    pass

connect_string = f'{POSTGRES_SYSTEM}+{POSTGRES_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}'

if LOG_LEVEL == LogLevelsEn.debug.value:
    engine = create_engine(connect_string, echo=True)
else:
    engine = create_engine(connect_string)

Session = sessionmaker(bind=engine)

users_message_text = 'Пользователей в базе данных: {number}'
plane_message_text = 'Рассылка запланирована ⌚\n\nuuid: {uuid}\nДата и время: {day}.{month}/{hour}:{minute}'
invalid_format_text = 'Не верный формат, попробуйте еще раз!'
file_change_text = 'Отправте файл на который вы хотите заменить текст.'
success_file_changed_text = 'Файл был успешно заменен!'
uuid_for_cancel_text = 'Введите uuid рассылки для ее отмены:'
success_update_status_text = 'Рассылка отменена!'
not_success_update_status_text = 'Не правильно введен uuid!'
choose_templates_text = 'Выберите какой из текстов вам надо заменить.'
plan_text = 'Теперь введите дату и время для планировки сообщения. В формате: DD.MM/HH:MM'

not_groups_log_text = 'Группы в БД не обнаружены, запуск сервиса не возможен...'

DATETIME_FORMAT = r'^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\/(0?[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$'