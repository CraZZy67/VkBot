from vk_api.bot_longpoll import VkBotEventType
from vk_api.vk_api import VkApiMethod

import logging
from math import ceil
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
from .constants import MAX_SYMBOLS, EVENT_WAIT
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
from .enums import (
    CommandsEn, 
    StatesEn, 
    CheckWordsEn, 
    TemplateNamesEn,
    JobStatusesEn
)


log = logging.getLogger(__name__)

def client_handl(group_id: int, user_info: dict, vk: VkApiMethod) -> None:
    if not user_in_db(group_id, user_info['user_id']):
        add_user(group_id, user_info)
        log.info(f'[{group_id}] Новый пользователь добавлен в БД: {user_info['user_id']}')

    group_template = get_template(group_id)[0]
    log.debug(f'[{group_id}] Template объект: {group_template}')

    if user_is_follower(group_id, user_info['user_id'], vk):
        subscribed = group_template[0]

        log.debug(f'[{group_id}] Sub text: {subscribed}')

        text_parts = ceil(len(subscribed) / MAX_SYMBOLS)

        for i in range(0, text_parts):
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0,
                message=subscribed[i * MAX_SYMBOLS:(i + 1) * MAX_SYMBOLS]
            )
    else:
        not_subscribed = group_template.not_subscribed[1]

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=not_subscribed, 
            keyboard=kb_not_subscribed()
        )

def admin_states_handl(group_id: int, user_info: dict, message, states: dict, vk: VkApiMethod) -> None:
    # cmd /clear handling 
    if message['text'] == CommandsEn.CLEAR.value:
        states[group_id] = ''

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message='Состояние отчищено.'
        )

    # schedule distribution state handling
    elif states.get(group_id) == StatesEn.PLANE_DIST:
        parsed_datetime = parse_datetime(message=message['text'])
        if parsed_datetime:
            states[group_id] = ''

            datetime_ = datetime(
                year=int(parsed_datetime['year']),
                month=int(parsed_datetime['month']),
                day=int(parsed_datetime['day']),
                hour=int(parsed_datetime['hour']),
                minute=int(parsed_datetime['minute'])
            )

            uuid_job = add_job(
                group_id=group_id, 
                user_id=user_info['user_id'], 
                datetime=datetime_
            )

            log.info(f'[{group_id}] Рассылка была запланирована на: {datetime_}')

            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=plane_message_text.format(
                    uuid=uuid_job,
                    month=parsed_datetime['month'],
                    day=parsed_datetime['day'],
                    hour=parsed_datetime['hour'],
                    minute=parsed_datetime['minute']
                )
            )
        else:
            log.info(f'[{group_id}] Введен не верный формат datetime: {message['text']}')
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0, 
                message=invalid_format_text
            )
    
    # change templates for group state hendling
    elif 'attachments' in message and states.get(group_id) in TemplateNamesEn:
        for attachment in message['attachments']:
            if attachment['type'] == 'doc':
                new_template_text = get_file(file_url=attachment['doc']['url'])

                log.info(f'[{group_id}] Файл для {states[group_id]} template: {attachment['doc']['url']}')

                update_template(
                    group_id=group_id,
                    field=states[group_id],
                    text=new_template_text
                )

                vk.messages.send(
                    user_id=user_info['user_id'], 
                    random_id=0, 
                    message=success_file_changed_text
                )

    # cancel distribution state handling
    elif states.get(group_id) == StatesEn.CANCEL:
        job = get_job(uuid=message['text'])
        if job:
            if job.status not in (JobStatusesEn.QUEUE, JobStatusesEn.PROCESS):
                update_job_status(uuid=message['text'])

                log.info(f'[{group_id}] Рассылка {message['text']}, была отменена')

                vk.messages.send(
                    user_id=user_info['user_id'], 
                    random_id=0,
                    message=success_update_status_text
                )

                states[group_id] = ''
            else:
                vk.messages.send(
                    user_id=user_info['user_id'], 
                    random_id=0,
                    message='Задача в процессе обработки, нельзя отменить!'
                )

                states[group_id] = ''
        else:
            vk.messages.send(
                user_id=user_info['user_id'], 
                random_id=0,
                message=not_success_update_status_text
            )

   
def admin_commands_handl(group_id: int, user_info: dict, message, states: dict, vk: VkApiMethod) -> None:
    # templates name messages for change handling
    if message['text'] in TemplateNamesEn:
        states[group_id] = message['text']

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0,
            message=file_change_text 
        )

    # cmd /user handling
    elif message['text'] == CommandsEn.USERS.value:
        log.debug(f'In cmd /users')
        number_user = get_number_users(group_id=group_id)

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=users_message_text.format(number=number_user), 
            keyboard=kb_users()
        )
    
    # cancel message handling
    elif message['text'] == CommandsEn.CANCEL_DIST.value:
        states[group_id] = StatesEn.CANCEL

        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=uuid_for_cancel_text
        )
    
    # cmd /change handling
    elif message['text'] == CommandsEn.CHANGE.value:
        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=choose_templates_text,
            keyboard=kb_templates()
        )
    
    # plane dist message handling
    elif message['text'] == CommandsEn.PLANE_DIST.value:
        states[group_id] = StatesEn.PLANE_DIST

        vk.messages.send(
            user_id=user_info['user_id'],
            random_id=0,
            message=plan_text,
        )

    # distribution now message handling 
    elif message['text'] == CommandsEn.DIST_NOW.value:
        now = datetime.now(timezone(timedelta(hours=3)))

        uuid_job = add_job(
            group_id=group_id, 
            user_id=user_info['user_id'], 
            datetime=now
        )

        log.info(f'[{group_id}] Рассылка была запланирована на текущее время: {now}')

        vk.messages.send(
            user_id=user_info['user_id'], 
            random_id=0, 
            message=plane_message_text.format(
                uuid=uuid_job,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=now.minute
            )
        )
    

def admin_handl(group_id: int, user_info: dict, message, states: dict, vk: VkApiMethod) -> None:
    log.debug(f'[{group_id}] Message: {message['text']}')

    try:
        admin_states_handl(group_id, user_info, message, states, vk)
        admin_commands_handl(group_id, user_info, message, states, vk)
    except Exception as ex:
        log.exception(f'[{group_id}] Ошибка админской стороны: {ex}')
        raise


def start_event_loop():
    groups_api = form_api_dict(groups_info=get_groups())
    longpool = BotsLongPollCust(bot_creds=groups_api, wait=0)

    states = {}

    for event in longpool.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_info = get_user_info(groups_api=groups_api, event=event)

                group_api = groups_api[event.group_id].get_api()
                log.debug(f'[{event.group_id}] Group: {event.group_id}, API: {group_api}')
                log.debug(f'[{event.group_id}] User: {user_info["user_id"]}, admins: {get_admins(group_id=event.group_id)}')

                if event.message['text'] in CheckWordsEn:
                    try:
                        client_handl(
                            group_id=event.group_id, 
                            user_info=user_info, 
                            vk=group_api
                        )
                    except Exception as ex:
                        log.exception(f'[{event.group_id}] Ошибка клиентской стороны: {ex}')
                        raise

                elif int(user_info['user_id']) in get_admins(group_id=event.group_id):
                    log.debug(f'[{event.group_id}] In admin')
                    admin_handl(
                        group_id=event.group_id,
                        user_info=user_info,
                        message=event.message,
                        states=states,
                        vk=group_api
                    )
        except Exception as ex:
            log.exception(f'Ошибка в event loop: {ex} group: {event.group_id}')
            continue