import logging
from time import sleep

from .event_loop import start_event_loop
from .config import Base, engine, not_groups_log_text
from .c_logger import configure_logging
from .service import get_groups, add_default_template, get_template


log = logging.getLogger(__name__)

def check_groups():
    while True:
        groups = get_groups()

        if not len(groups):
            log.info(not_groups_log_text)
        else:
            break

        sleep(30.0)

def create_templates():
    groups = get_groups()

    for group in groups:
        if not get_template(group_id=group[0]):
            add_default_template(group_id=group[0])

def main():
    configure_logging()

    Base.metadata.create_all(bind=engine)

    check_groups()
    create_templates()

    log.info('Сервис запущен!')
    start_event_loop()

if __name__ == '__main__':
    main()