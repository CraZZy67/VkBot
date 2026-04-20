import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEvent


class BotsLongPollCust(VkBotLongPoll):

    def __init__(self, bot_creds: dict[int, VkApi], wait=25):
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

            response = self.bot_creds[id_].method('groups.getLongPollServer', values)

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
                self.url,
                params=values,
                timeout=self.wait + 10
            ).json()

            if 'failed' not in response:
                bot_info['ts'] = response['ts']
                event_list.extend([
                    self._parse_event(raw_event)
                    for raw_event in response['updates']
                ])

            elif response['failed'] == 1:
                bot_info['ts'] = response['ts']

            elif response['failed'] == 2:
                self.update_longpoll_server(update_ts=False)

            elif response['failed'] == 3:
                self.update_longpoll_server()
        
        return event_list