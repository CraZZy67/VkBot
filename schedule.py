from vk_api import VkApi

from datetime import timezone, datetime, timedelta
import time
import sys

import modules
from settings import settings1


vk_session = VkApi(token=settings1.TOKEN)
vk = vk_session.get_api()

def schedule_message(day: str, month: str, hours: str, minutes: str, user_id):
    now = datetime.now(timezone(timedelta(hours=3)))
    target = datetime.fromisoformat(f"{now.year}-{month}-{day} {hours}:{minutes}:00")
    target = target.replace(tzinfo=timezone(timedelta(hours=3)))

    diff = target - now

    print(f'Ожидаем: {diff}')

    if diff.total_seconds() > 0:
        time.sleep(diff.total_seconds())
        print('Проснулся!')

    modules.distribution_text(vk=vk, user_id=int(user_id))

if __name__ == '__main__':
    schedule_message(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        sys.argv[4],
        sys.argv[5]
    )