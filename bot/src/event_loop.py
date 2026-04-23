from vk_api.bot_longpoll import VkBotEventType

from .utils import form_api_dict, get_user_info
from .service import get_groups
from .long_pooll import BotsLongPollCust


def start_event_loop():
    groups_api = form_api_dict(groups_info=get_groups())
    longpool = BotsLongPollCust(bot_creds=form_api_dict(groups_info=groups_api))

    states = {}

    for event in longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_info = get_user_info(groups_api=groups_api, event=event)