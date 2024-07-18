import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv

import os

load_dotenv()


def get_text(file: str) -> str:
    with open(file, encoding="utf-8") as f:
        return "".join(f.readlines())


def main():
    trigger_words_s = [
                        "начать", "start", "/start", "/начать", "Начать", "Start"
                        "Я подписался!", "я подписался", "Я подписался", "я подписался!"
                       ]

    vk_session = vk_api.VkApi(token=os.getenv("TOKEN"))
    longpoll = VkBotLongPoll(vk_session, os.getenv("GROUP_ID"))
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] in trigger_words_s:
            id_ = event.obj.message["from_id"]

            if vk.groups.isMember(group_id=os.getenv("GROUP_ID"), user_id=id_):
                vk.messages.send(user_id=id_, random_id=0, message=get_text("texts/follow.txt"))
            else:
                kb = VkKeyboard(one_time=False, inline=True)
                kb.add_button(color=VkKeyboardColor.POSITIVE, label="Я подписался")

                vk.messages.send(user_id=id_, random_id=0, message=get_text("texts/un_follow.txt"),
                                 keyboard=kb.get_keyboard())


if __name__ == '__main__':
    print("Бот запущен!")
    main()
