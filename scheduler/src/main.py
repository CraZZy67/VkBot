import logging

from .c_logger import configure_logging
from .loop import start_loop


log = logging.getLogger(__name__)

def main():
    configure_logging()
    log.info('Сервис запущен!')
    start_loop()

if __name__ == '__main__':
    main()