from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import modules
from settings import settings1

vk_session = VkApi(token=settings1.TOKEN)
longpoll = VkBotLongPoll(vk_session, settings1.GROUP_ID)
vk = vk_session.get_api()


def main():
    state = ""

    while True:
        try:
            for event in longpoll.listen():

                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_id = event.obj.message["from_id"]

                    if event.obj.message["text"] in settings1.WORDS:
                        modules.add_user(user_id)
                        modules.check_follow(vk=vk, group_id=settings1.GROUP_ID, user_id=user_id)

                    if str(user_id) in settings1.ADMINS.split(","):

                        if event.obj.message["text"] == "/users":
                            text = f"Пользователей в базе данных: {modules.get_len_db()}"
                            vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=modules.kb_db_info())
                            modules.main_logger.info("Информация о БД отправлена в диалог.")

                        if event.obj.message["text"] == "Отчистить базу данных":
                            modules.clear_db()
                            vk.messages.send(user_id=user_id, random_id=0, message="База данных отчищена")

                        if event.obj.message["text"] == "Разослать сообщение":
                            modules.distribution_text(vk=vk, user_id=user_id)

                        if event.obj.message["text"] == "/change":
                            state = "change"
                            text = "Выберите какой из текстов вам надо заменить."
                            vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=modules.kb_texts())

                        if event.obj.message["text"] in modules.buttons and state == "change":
                            state = event.obj.message["text"]
                            text = "Отправте файл на который вы хотите заменить текст."
                            vk.messages.send(user_id=user_id, random_id=0, message=text)

                        if 'attachments' in event.obj.message and state in modules.buttons:
                            for attachment in event.obj.message['attachments']:
                                if attachment['type'] == 'doc':
                                    state = modules.handling_docs(vk, attachment, state)
                                    vk.messages.send(user_id=user_id, random_id=0, message="Файл был успешно заменён!")

        except Exception as ex:
            modules.main_logger.error(f"Произошла неожиданная ошибка: {ex}")
            state = ""
            continue


if __name__ == '__main__':
    modules.main_logger.info("Бот запущен!")
    main()
