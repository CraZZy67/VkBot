from enum import StrEnum
import logging

from .constants import LOG_LEVEL


LOG_FORMAT = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"

class LogLevelsEn(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"

def configure_logging():
    log_level = LOG_LEVEL.upper()

    if log_level in LogLevelsEn:
        logging.basicConfig(level=log_level, format=LOG_FORMAT)
        return
    else:
        logging.basicConfig(level=LogLevelsEn.info.value, format=LOG_FORMAT)
        return