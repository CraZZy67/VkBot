import requests
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod

import re
from datetime import datetime

from .config import DATETIME_FORMAT


def form_api_dict(groups_info: list[list[int, str]]) -> dict[int, VkApi]:
    api_dict = dict()

    for info in groups_info:
        api_dict[info[0]] = VkApi(token=info[1])
    
    return api_dict

def get_user_info(groups_api: dict, event) -> dict:
    user_id = event.obj.message["from_id"]

    parametrs = {
        "user_ids": user_id, 
        "fields": "first_name,last_name"
    }

    user_names = groups_api[event.group_id].method("users.get", parametrs)

    return {
        "user_id": user_id,
        "first_name": user_names[0].get("first_name"),
        "last_name": user_names[0].get("last_name")
    }

def user_is_follower(group_id: int, user_id: int, vk: VkApiMethod) -> bool:
    return True if vk.groups.isMember(group_id=group_id, user_id=user_id) else False

def parse_datetime(message: str) -> dict:
    match = re.fullmatch(DATETIME_FORMAT, message)

    if match:
        return {
            'year': datetime.now().year,
            'month': match.group(1),
            'day': match.group(2),
            'hour': match.group(3),
            'second': match.group(4),
        }
    else:
        return {}

def get_file(file_url: str) -> str:
    response = requests.get(file_url)
    response.encoding = 'utf-8'
    return response.text
