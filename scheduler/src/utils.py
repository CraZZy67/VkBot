from datetime import datetime

from .constants import SECONDS_IN_MINUTE, MIN_DIFF_MNNUTE

def check_diff(current_datetime: datetime, check_datetime: datetime) -> bool:
    time_del = check_datetime - current_datetime

    if time_del.days < 0:
        time_del = current_datetime - check_datetime

    minute_timedel = time_del.seconds // int(SECONDS_IN_MINUTE)
    return True if minute_timedel >= int(MIN_DIFF_MNNUTE) else False

def check_current_job(current_job: tuple, jobs: list) -> bool:
    for check_job in jobs:
        if current_job[1] != check_job[1]:
            if not check_diff(current_job[2], check_job[2]):
                return False
    return True
