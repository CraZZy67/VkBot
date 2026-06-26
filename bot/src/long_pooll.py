import requests
from vk_api import VkApi
from vk_api.exceptions import ApiError
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEvent

import logging
from time import sleep

from .constants import EVENT_WAIT


log = logging.getLogger(__name__)

class BotsLongPollCust(VkBotLongPoll):

    def __init__(self, bot_creds: dict[int, VkApi], wait=10):
        self.bot_creds = bot_creds
        self.wait = wait

        self.lng_pool_bots_info = {}

        for id_ in bot_creds.keys():
            self.lng_pool_bots_info[id_] = {
                'url': None,
                'key': None,                
                'server': None,
                'ts': None
            }

        self.session = requests.Session()

        self.update_longpoll_server()
    
    def update_longpoll_server(self, update_ts=True):
        for id_ in self.bot_creds.keys():
            values = {
                'group_id': id_
            }

            try:
                response = self.bot_creds[id_].method('groups.getLongPollServer', values)
            except ApiError as ex:
                log.exception(f'Ошибка получения long_poll сервера для группы {id_}: {ex}')
                continue

            self.lng_pool_bots_info[id_]['key'] = response['key']
            self.lng_pool_bots_info[id_]['server'] = response['server']

            self.url = self.lng_pool_bots_info[id_]['server']

            if update_ts:
                self.lng_pool_bots_info[id_]['ts'] = response['ts']
    
    def check(self) -> list[VkBotEvent]:
        event_list: list = list()

        for bot_info in self.lng_pool_bots_info.values():
            values = {
                'act': 'a_check',
                'key': bot_info['key'],
                'ts': bot_info['ts'],
                'wait': self.wait,
            }

            response = self.session.get(
                bot_info['server'],
                params=values,
                timeout=self.wait + 10
            ).json()

            if 'failed' not in response:
                bot_info['ts'] = response['ts']
                event_list.extend([
                    self._parse_event(raw_event)
                    for raw_event in response['updates']
                ])

            elif response.get('failed') == 1:
                bot_info['ts'] = response.get('ts')

            elif response.get('failed') == 2:
                self.update_longpoll_server(update_ts=False)

            elif response.get('failed') == 3:
                self.update_longpoll_server()
        
        log.debug(f'event list: {event_list}')
        return event_list
    
    def listen(self):
        while True:
            sleep(float(EVENT_WAIT))
            yield from self.check()