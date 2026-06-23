from vk_api import VkApi
from vk_api.exceptions import ApiError


import json
import logging
from math import ceil
from time import sleep

from .utils import format_template
from .service import (
    get_users, 
    get_template, 
    get_group_token,
    get_job_info, 
    del_users, 
    update_status
)
from .config import redis, feedback_text
from .constants import REDIS_QUEUE_NAME, WORKER_LOOP_WAIT, MAX_SYMBOLS
from .enums import JobStatusesEn


log = logging.getLogger(__name__)

def job_handl(job: dict) -> None:
    template = get_template(job['group_id'])
    vk = VkApi(token=get_group_token(job['group_id'])).get_api()
    blocked_users = []

    update_status(job['uuid'], JobStatusesEn.PROCESS.value)
    log.info(f'Запуск рассылки задачи {job['uuid']}, группы {job['group_id']}')

    for user in get_users(job['group_id']):
        template = format_template(template, user)

        template_parts = ceil(len(template) / MAX_SYMBOLS)

        try:
            for i in range(0, template_parts):
                vk.messages.send(
                    user_id=user.user_id, 
                    random_id=0,
                    message=template[i * MAX_SYMBOLS:(i + 1) * MAX_SYMBOLS]
                )
        except ApiError as ex:
            if ex.code == 901:
                blocked_users.append(user.user_id)
                log.info(f'Пользователь {user.user_id} заблокировал бота')
            else:
                log.exception(f'Ошибка отправки сообщения: {ex}')

        log.info(f'Сообщение пользователю {user.user_id} отправлено')
    
    del_users(job['group_id'], blocked_users)
    update_status(job['uuid'], JobStatusesEn.DONE.value)

    log.info(f'Рассылка задачи {job['uuid']}, группы {job['group_id']} завершена!')

    job_info = get_job_info(job['uuid'])
    vk.messages.send(user_id=job_info[0], random_id=0,
                        message=feedback_text.format(date=job_info[1], count=len(blocked_users)))

def start_loop() -> None:
    while True:
        log.info('Ожидание задачи...')
        try:
            job = json.loads(redis.brpop(REDIS_QUEUE_NAME)[1])
            job_handl(job)
        except Exception as ex:
            log.exception(f'Ошибка при обработки задачи {job['uuid']}: {ex}')

        sleep(float(WORKER_LOOP_WAIT))