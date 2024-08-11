from vk_api.vk_api import VkApiMethod

from modules.logger import main_logger
from modules.keyboards import kb_un_follow
from settings import settings1

from math import ceil
from typing import Union


def add_user(user_id: str) -> None:
    attend = False
    with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
        lines = f.readlines()

        for i in lines:
            i = i[0:-1]
            if str(user_id) == i:
                attend = True
                main_logger.info(f"Пользователь уже есть в БД id: {user_id}")

    if not attend:
        with open(settings1.PATH_DB, "a", encoding="utf-8") as f:
            f.write(str(user_id) + "\n")
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


def get_ids() -> Union[list, str]:
    ids_list = list()
    if get_len_db() <= 100:
        with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
            return ",".join(f.readlines()).replace("\n", "")

    else:
        count = int()
        str_ = str()

        with open(settings1.PATH_DB, "r", encoding="utf-8") as f:
            for i in f.readlines():
                count += 1
                if count != 101:
                    str_ += f"{i[0:-1]},"

                else:
                    ids_list.append(str_[0:-1])
                    count = int()
                    str_ = str()

    return ids_list


def count_error_users(response: dict):
    error_users = int()

    for i in response:
        try:
            if i["error"]["code"] in [900, 901]:
                error_users += 1
        except KeyError:
            continue
    return error_users


def distribution_text(vk: VkApiMethod, user_id: int) -> None:
    ids = get_ids()
    response = list()

    text = get_text(settings1.PATH_DISTRIBUTION)
    len_text = len(text)
    counter = ceil(len_text / 4096)

    if isinstance(ids, str):
        for i in range(0, counter):
            response = vk.messages.send(user_ids=ids, random_id=0, message=text[i * 4096:(i + 1) * 4096])

        error_users = count_error_users(response)

        main_logger.info("Меньше ста сообщений разослано!")
        vk.messages.send(user_id=user_id, random_id=0,
                         message=f"Сообщение разослано. Не удалось отправить: {error_users}")

    elif isinstance(ids, list):
        error_users = int()
        for i in get_ids():
            for k in range(0, counter):
                response = vk.messages.send(user_ids=i, random_id=0, message=text[k * 4096:(k + 1) * 4096])

            error_users += count_error_users(response)

        main_logger.info("Больше ста сообщений разослано!")
        vk.messages.send(user_id=user_id, random_id=0,
                         message=f"Сообщение разослано. Не удалось отправить: {error_users}")
