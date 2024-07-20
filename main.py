import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv

import os
from typing import Union

from loger import main_logger

load_dotenv()

trigger_words_s = [
    "начать", "start", "/start", "/начать", "Начать", "Start"
    "Я подписался!", "я подписался", "Я подписался", "я подписался!"
]

admins = [521427402]


def get_text(file: str) -> str:
    with open(file, encoding="utf-8") as f:
        return "".join(f.readlines())


def get_len_db() -> int:
    with open("data/users_db.csv", "r", encoding="utf-8") as f:
        return len(f.readlines())


def get_ids() -> Union[str, list]:
    with open("data/users_db.csv", "r", encoding="utf-8") as f:
        ids_list = []
        if get_len_db() < 100:
            return ",".join(f.readlines()).replace("\n", "")
        else:
            with open("data/users_db.csv", "r", encoding="utf-8") as file:
                count = 0
                str_r = ""
                for i in file.readlines():
                    count += 1
                    if count != 100:
                        str_r += f"{i[0:-1]},"
                    else:
                        ids_list.append(str_r[0:-1])
                        count = 0
                        str_r = ""
                return ids_list


def add_user(user_id: str):
    attend = False
    with open("data/users_db.csv", "r", encoding="utf-8") as f:
        lines = f.readlines()

        if len(lines) > 0:
            for i in lines:
                i = i[0:-1]
                if user_id == i:
                    attend = True
                    main_logger.info(f"Пользователь уже есть в БД id: {user_id}")

    if not attend:
        with open("data/users_db.csv", "a", encoding="utf-8") as f:
            f.write(user_id + "\n")
            main_logger.info(f"Пользователь добавлен в БД id: {user_id}")


def clear_db():
    with open("data/users_db.csv", "w", encoding="utf-8") as f:
        f.write("")


def main():
    vk_session = vk_api.VkApi(token=os.getenv("TOKEN"))
    longpoll = VkBotLongPoll(vk_session, os.getenv("GROUP_ID"))
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] in trigger_words_s:
            id_ = event.obj.message["from_id"]
            add_user(str(id_))

            if vk.groups.isMember(group_id=os.getenv("GROUP_ID"), user_id=id_):
                vk.messages.send(user_id=id_, random_id=0, message=get_text("texts/follow.txt"))
                main_logger.info(f"Пользователь {id_} подписан, продолжение отправлено.")
            else:
                kb = VkKeyboard(one_time=False, inline=True)
                kb.add_button(color=VkKeyboardColor.POSITIVE, label="Я подписался")

                vk.messages.send(user_id=id_, random_id=0, message=get_text("texts/un_follow.txt"),
                                 keyboard=kb.get_keyboard())
                main_logger.info(f"Пользователь {id_} не подписан")

        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] == "/users":
            id_ = event.obj.message["from_id"]
            if id_ in admins:
                kb2 = VkKeyboard(one_time=False, inline=True)
                kb2.add_button(color=VkKeyboardColor.NEGATIVE, label="Отчистить базу данных")
                kb2.add_button(color=VkKeyboardColor.POSITIVE, label="Разослать сообщение")

                vk.messages.send(user_id=id_, random_id=0, message=f"Пользователей в базе данных: {get_len_db()}",
                                 keyboard=kb2.get_keyboard())
                main_logger.info("Информация о БД отправлена в диалог.")

        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] == "Отчистить базу данных":
            id_ = event.obj.message["from_id"]
            if id_ in admins:
                clear_db()
                main_logger.info("База данных отчищена")
                vk.messages.send(user_id=id_, random_id=0, message="База данных отчищена")

        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message["text"] == "Разослать сообщение":
            id_ = event.obj.message["from_id"]
            if id_ in admins:
                if get_len_db() < 100 and get_len_db() != 0:
                    vk.messages.send(user_ids=get_ids(), random_id=0, message=get_text("texts/distribution.txt"),
                                     dont_parse_links=0)
                    main_logger.info("Меньше ста сообщений разослано!")

                elif get_len_db() >= 100:
                    for i in get_ids():
                        vk.messages.send(user_ids=i, random_id=0,
                                         message=get_text("texts/distribution.txt"),
                                         dont_parse_links=0)
                    main_logger.info("Больше ста сообщений разослано!")


if __name__ == '__main__':
    main_logger.info("Бот запущен!")
    main()
