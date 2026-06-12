from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiMethod

from datetime import datetime, timezone, timedelta

from .utils import (
    form_api_dict, 
    get_user_info, 
    user_is_follower, 
    parse_datetime,
    get_file
)
from .service import (
    get_groups, 
    get_admins, 
    user_in_db, 
    add_user, 
    get_template, 
    add_job, 
    get_number_users,
    update_template,
    get_job,
    update_job_status
)
from .keyboards import kb_not_subscribed, kb_users, kb_templates
from .constants import MAX_SYMBOLS
from .config import (
    users_message_text, 
    plane_message_text, 
    invalid_format_text,
    file_change_text,
    success_file_changed_text,
    uuid_for_cancel_text,
    success_update_status_text,
    not_success_update_status_text,
    choose_templates_text,
    plan_text
)
from .long_pooll import BotsLongPollCust
from .enums import CommandsEn, StatesEn, CheckWordsEn, TemplateNames


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

def admin_handl(group_id: int, user_info: dict, message, state: str, vk: VkApiMethod) -> None:
    if state == StatesEn.PLANE_DIST:
        parsed_datetime = parse_datetime(message=message['text'])
        if parsed_datetime:
            state[group_id] = ''

            datetime_ = datetime(
                year=parsed_datetime['year'],
                month=parsed_datetime['month'],
                day=parsed_datetime['day'],
                minute=parsed_datetime['minute'],
                second=parsed_datetime['second']
            )

            uuid_job = add_job(
                group_id=group_id, 
                user_id=user_info['user_id'], 
                datetime=datetime_
            )

            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=plane_message_text.format(
                    uuid=uuid_job,
                    month=parsed_datetime['month'],
                    day=parsed_datetime['day'],
                    minute=parsed_datetime['minute'],
                    second=parsed_datetime['second']
                )
            )
        else:
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=invalid_format_text
            )
        
    if message['text'] in TemplateNames:
        state[group_id] = message['text']

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0,
            message=file_change_text 
        )
    
    if 'attachments' in message and state in TemplateNames:
        for attachment in message['attachments']:
            if attachment['type'] == 'doc':
                new_template_text = get_file(file_url=attachment['doc']['url'])
                update_template(
                    group_id=group_id,
                    field=state,
                    text=new_template_text
                )

                state[group_id] = ''

                vk.messages.send(
                    user_id=user_info['user_id'], 
                    random_id=0, 
                    message=success_file_changed_text
                )

    if state == StatesEn.CANCEL:
        if get_job(uuid=message['text']):
            update_job_status(uuid=message['text'])

            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0,
                message=success_update_status_text
            )
        else:
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0,
                message=not_success_update_status_text
            )

    if message['text'] == CommandsEn.USERS:
        number_user = get_number_users(group_id=group_id)

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=users_message_text.format(number=number_user), 
            keyboard=kb_users()
        )
    
    if message['text'] == CommandsEn.CANCEL_DIST:
        state[group_id] == StatesEn.CANCEL

        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=uuid_for_cancel_text
        )
    
    if message['text'] == CommandsEn.CHANGE:
        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=choose_templates_text,
            keyboard=kb_templates()
        )
    
    if message['text'] == CommandsEn.PLANE_DIST:
        state[group_id] == StatesEn.PLANE_DIST

        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=plan_text,
        )
    
    if message['text'] == CommandsEn.DIST_NOW:
        now = datetime.now(timezone(timedelta(hours=3)))

        add_job(
            group_id=group_id, 
            user_id=user_info['user_id'], 
            datetime=now
        )

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=plane_message_text.format(
                uuid=uuid_job,
                month=now.month,
                day=now.day,
                minute=now.minute,
                second=now.second
            )
        )

def start_event_loop():
    groups_api = form_api_dict(groups_info=get_groups())
    longpool = BotsLongPollCust(bot_creds=form_api_dict(groups_info=groups_api))

    states = {}

    for event in longpool.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_info = get_user_info(groups_api=groups_api, event=event)
            if event.message['text'] in CheckWordsEn:
                client_handl(
                    group_id=event.group_id, 
                    user_info=user_info, 
                    vk=groups_api[event.group_id].get_api()
                )
            elif user_info['user_id'] in get_admins(group_id=event.group_id):
                admin_handl(
                    group_id=event.group_id,
                    user_info=user_info,
                    message=event.message,
                    state=states,
                    vk=groups_api[event.group_id].get_api()
                )