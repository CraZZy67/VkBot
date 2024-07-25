from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from sup_functions import *
from keyboards import kb_db_info

vk_session = VkApi(token=settings1.TOKEN)
longpoll = VkBotLongPoll(vk_session, settings1.GROUP_ID)
vk = vk_session.get_api()


def main():
    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message["from_id"]

            if event.obj.message["text"] in settings1.WORDS:
                add_user(user_id)
                check_follow(vk=vk, group_id=settings1.GROUP_ID, user_id=user_id)

            if str(user_id) in settings1.ADMINS.split(","):

                if event.obj.message["text"] == "/users":
                    text = f"Пользователей в базе данных: {get_len_db()}"
                    vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=kb_db_info())
                    main_logger.info("Информация о БД отправлена в диалог.")

                if event.obj.message["text"] == "Отчистить базу данных":
                    clear_db()
                    vk.messages.send(user_id=user_id, random_id=0, message="База данных отчищена")

                if event.obj.message["text"] == "Разослать сообщение":
                    distribution_text(vk=vk, user_id=user_id)


try:

    if __name__ == '__main__':
        main_logger.info("Бот запущен!")
        main()

except Exception as ex:
    main_logger.exception(f"Произошла неожиданная ошибка: {ex}")
    main()
