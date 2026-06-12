from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiMethod

from datetime import datetime

from .utils import (
    form_api_dict, 
    get_user_info, 
    user_is_follower, 
    parse_datetime
)
from .service import (
    get_groups, 
    get_admins, 
    user_in_db, 
    add_user, 
    get_template, 
    add_job, 
    get_number_users
)
from .keyboards import kb_not_subscribed, kb_users
from .constants import MAX_SYMBOLS
from .config import (
    CHECK_WORDS, 
    users_message_text, 
    plane_message_text, 
    invalid_format_text
)
from .long_pooll import BotsLongPollCust
from .enums import CommandsEn, StatesEn


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

def admin_handl(group_id: int, user_info: dict, message: str, state: str, vk: VkApiMethod) -> None:
    if state == StatesEn.PLANE_DIST:
        parsed_datetime = parse_datetime(message=message)
        if parsed_datetime:
            state[group_id] = ''

            datetime_ = datetime(
                year=parsed_datetime['year'],
                month=parsed_datetime['month'],
                day=parsed_datetime['day'],
                second=parsed_datetime['second']
            )

            uuid_job = add_job(group_id=group_id, datetime=datetime_)

            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=plane_message_text.format(
                    uuid=uuid_job,
                    month=parsed_datetime['month'],
                    day=parsed_datetime['day'],
                    second=parsed_datetime['second']
                )
            )
        else:
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=invalid_format_text
            )
        
    if state == StatesEn.CHANGE:
        ...

    if message == CommandsEn.USERS:
        number_user = get_number_users(group_id=group_id)

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=users_message_text.format(number=number_user), 
            keyboard=kb_users()
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