from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from settings import settings1

vk_session = VkApi(token=settings1.TOKEN)
longpoll = VkBotLongPoll(vk_session, settings1.GROUP_ID)
vk = vk_session.get_api()


def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            ...
