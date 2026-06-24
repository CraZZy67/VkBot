from sqlalchemy.orm import DeclarativeBase

from .constants import (
    POSTGRES_DRIVER,
    POSTGRES_HOST_NAME,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SYSTEM,
    POSTGRES_USER,
)

class Base(DeclarativeBase): 
    pass

connect_string = f'{POSTGRES_SYSTEM}+{POSTGRES_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST_NAME}:{POSTGRES_PORT}/{POSTGRES_DB}'

