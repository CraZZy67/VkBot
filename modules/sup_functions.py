from vk_api.vk_api import VkApiMethod

from modules.logger import main_logger
from modules.keyboards import kb_un_follow
from settings import settings1

from functools import reduce
from math import ceil
from typing import Union


def add_user(user_id: int, user_first_name: str, user_last_name: str) -> None:
    attend = False
    with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
        lines = f.readlines()

        for i in lines:
            i = i[0:-1]
            if user_id == i:
                attend = True
                main_logger.info(f"Пользователь уже есть в БД id: {user_id}")

    if not attend:
        with open(settings1.PATH_DB, "a", encoding="utf-8") as f:
            f.write("{0},{1},{2}\n".format(user_id, user_first_name, user_last_name))
            main_logger.info(f"Пользователь добавлен в БД id: {user_id}")


def get_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return "".join(f.readlines())


def check_follow(vk: VkApiMethod, group_id: str, user_id: int) -> None:
    if vk.groups.isMember(group_id=group_id, user_id=user_id):
        text = get_text(settings1.PATH_FOLLOW)
        len_text = len(text)
        counter = ceil(len_text / 4096)

        for i in range(0, counter):
            vk.messages.send(user_id=user_id, random_id=0, message=text[i * 4096:(i + 1) * 4096])

        main_logger.info(f"Пользователь {user_id} подписан, продолжение отправлено.")
    else:

        text = get_text(settings1.PATH_UN_FOLLOW)
        vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=kb_un_follow())
        main_logger.info(f"Пользователь {user_id} не подписан")


def get_len_db() -> int:
    with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
        return len(f.readlines())


def clear_db() -> None:
    with open(settings1.PATH_DB, "w", encoding="utf-8") as f:
        f.write("")
    main_logger.info("База данных отчищена")

def get_user_info(user_id: int) -> list:
    with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
        for i in f:
            if int(i.split(",")[0]) == user_id:
                return i.strip().split(",")[1:]
            
def text_formatting(text: str, user_id: int):
    user_info = get_user_info(user_id=user_id)
    
    if "first_name" in text and "last_name" in text:
        return text.format(first_name=user_info[0], last_name=user_info[1])
    
    elif "{first_name}" in text: 
        return text.format(first_name=user_info[0])
        
    elif "{last_name}" in text: 
        return text.format(last_name=user_info[1])
    
    return text

def get_ids() -> list:
    with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
        return [i.split(",")[0] for i in f]

def distribution_text(vk: VkApiMethod, user_id: int) -> None:
    ids = get_ids()
    text = get_text(settings1.PATH_DISTRIBUTION)
    len_text = len(text)
    counter = ceil(len_text / 4096)
    error_users = int()
        
    for i in ids:
        for k in range(0, counter):
            text = text_formatting(text=text, user_id=int(i))
            response = vk.messages.send(user_id=int(i), random_id = 0, message=text[k * 4096:(k + 1) * 4096])

        error_users += 0 if isinstance(response, int) else 1

    vk.messages.send(user_id=user_id, random_id=0,
                        message=f"Сообщение разослано. Не удалось отправить: {error_users}")
