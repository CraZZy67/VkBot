import json
from datetime import datetime, timezone, timedelta

from .service import get_groups, get_jobs, del_job, update_status
from .utils import check_current_job
from .enums import JobStatusesEn
from .config import redis
from .constants import REDIS_QUEUE_NAME


def jobs_handl(group_id: int, jobs: list[tuple]) -> None:
    for current_job in jobs:
        if current_job[3] in (JobStatusesEn.CANCEL, JobStatusesEn.DONE):
            del_job(current_job[1])
            continue

        if check_current_job(current_job, jobs):        
            datetime_diff = current_job[2] - datetime.now(timezone(timedelta(hours=3)))
            if datetime_diff.days < 0:
                req_payload = {
                    'group_id': group_id,
                    'uuid': current_job[1]
                }

                redis.lpush(REDIS_QUEUE_NAME, json.dumps(req_payload))
                update_status(current_job[1], JobStatusesEn.QUEUE)
        else:
            del_job(current_job[1])
            
        jobs.remove(current_job)
                

def start_loop() -> None:
    for group in get_groups():
        jobs = get_jobs(group)
        jobs.reverse()

        jobs_handl(group_id=group, jobs=jobs)