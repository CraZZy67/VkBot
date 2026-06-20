import logging
import json
import time
from datetime import datetime, timezone, timedelta

from .service import get_groups, get_jobs, del_job, update_status
from .utils import check_current_job
from .enums import JobStatusesEn
from .config import redis
from .constants import REDIS_QUEUE_NAME, SCHEDULER_LOOP_WAIT


log = logging.getLogger(__name__)

def jobs_handl(group_id: int, jobs: list[tuple]) -> None:
    for current_job in jobs:
        job_datetime = current_job[2].replace(tzinfo=timezone(timedelta(hours=3)))

        if current_job[3] in (JobStatusesEn.CANCEL, JobStatusesEn.DONE):
            del_job(current_job[1])
            
            log.info(f'Статус {current_job[3]} обнаружен, задача {current_job[1]} группы {group_id} удалена')
            continue
        
        if current_job[3] in (JobStatusesEn.QUEUE, JobStatusesEn.PROCESS):
            continue

        if check_current_job(current_job, jobs):
            datetime_diff = job_datetime - datetime.now(timezone(timedelta(hours=3)))
            if datetime_diff.days < 0:
                req_payload = {
                    'group_id': group_id,
                    'uuid': current_job[1]
                }

                try:
                    redis.lpush(REDIS_QUEUE_NAME, json.dumps(req_payload))
                except Exception as ex:
                    log.exception(f'Ошибка при работе с Redis: {ex}')
                    raise

                update_status(current_job[1], JobStatusesEn.QUEUE)

                log.info(f'Задача {current_job[1]} группы {group_id} отправлена в очередь')
        else:
            del_job(current_job[1])
            log.info(f'Задача {current_job[1]} группы {group_id} не валидна, удалена')

        jobs.remove(current_job)
                

def start_loop() -> None:
    while True:
        try:
            for group in get_groups():
                try:
                    jobs = get_jobs(group[0])
                    jobs.reverse()

                    jobs_handl(group_id=group[0], jobs=jobs)
                except Exception as ex:
                    log.exception(f'Ошибка при обработки группы {group[0]}: {ex}')
                    continue
        except Exception as ex:
            log.exception(f'Ошибка запуска цикла для групп: {ex}')
        
        log.debug(f'Ожидаю {SCHEDULER_LOOP_WAIT} сек...')
        time.sleep(float(SCHEDULER_LOOP_WAIT))