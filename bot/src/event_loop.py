from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiMethod

from .utils import form_api_dict, get_user_info, user_is_follower
from .service import get_groups, get_admins, user_in_db, add_user, get_template
from .constants import CHECK_WORDS, MAX_SYMBOLS
from .long_pooll import BotsLongPollCust
from .keyboards import kb_not_subscribed


def client_handl(group_id: int, user_info: dict, vk: VkApiMethod) -> None:
    if not user_in_db(group_id, user_info['user_id']):
        add_user(group_id, user_info)

    group_template = get_template(group_id)

    if user_is_follower(group_id, user_info['user_id'], vk):
        subscribed = group_template.subscribed

        text_parts = round(len(subscribed) / MAX_SYMBOLS)

        for i in range(0, text_parts):
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0,
                message=subscribed[i * MAX_SYMBOLS:(i + 1) * MAX_SYMBOLS]
            )
    else:
        not_subscribed = group_template.not_subscribed

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=not_subscribed, 
            keyboard=kb_not_subscribed()
        )

def start_event_loop():
    groups_api = form_api_dict(groups_info=get_groups())
    longpool = BotsLongPollCust(bot_creds=form_api_dict(groups_info=groups_api))

    states = {}

    for event in longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_info = get_user_info(groups_api=groups_api, event=event)
            if event.message['text'] in CHECK_WORDS:
                client_handl(
                    event.group_id, 
                    user_info, 
                    groups_api[event.group_id].get_api()
                )
            elif user_info['user_id'] in get_admins(group_id=event.group_id):
                ...