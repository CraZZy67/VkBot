import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv

import os

load_dotenv()


def main():

    vk_session = vk_api.VkApi(token=os.getenv("TOKEN"))
    longpoll = VkBotLongPoll(vk_session, os.getenv("GROUP_ID"))
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] == "start":
            id_ = event.obj.message["from_id"]
            kb = VkKeyboard(one_time=False, inline=True)
            kb.add_button(color=VkKeyboardColor.POSITIVE, label="Я подписался!")
            vk.messages.send(user_id=id_, random_id=0, message="Добро пожаловать", keyboard=kb.get_keyboard())


if __name__ == '__main__':
    print("Бот запущен!")
    main()
