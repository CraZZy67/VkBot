from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import subprocess

import modules
from settings import settings1

vk_session = VkApi(token=settings1.TOKEN)
longpoll = VkBotLongPoll(vk_session, settings1.GROUP_ID)
vk = vk_session.get_api()

def main():
    result = None
    process = None
    state = ""
    
    while True:
        try:
           for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.obj.message["from_id"]
                
                user_info = vk_session.method("users.get", {"user_ids": user_id, "fields": "first_name,last_name"})
                
                user_first_name = user_info[0]["first_name"] if "first_name" in user_info[0] else None
                user_last_name = user_info[0]["last_name"] if "last_name" in user_info[0] else None

                if event.obj.message["text"] in settings1.WORDS:
                    modules.add_user(str(user_id), str(user_first_name), str(user_last_name))
                    modules.check_follow(vk=vk, group_id=settings1.GROUP_ID, user_id=user_id)

                if str(user_id) in settings1.ADMINS.split(","):

                    if event.obj.message["text"] == "/users":
                        text = f"Пользователей в базе данных: {modules.get_len_db()}"
                        vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=modules.kb_db_info())
                        modules.main_logger.info("Информация о БД отправлена в диалог.")

                    if state == "Запланировать":
                        result = modules.sup_functions.check_datetime(event.obj.message["text"])

                        if result:
                            state = ""
                            
                            process = subprocess.Popen([
                                'venv/bin/python',
                                'schedule.py',
                                result[0],
                                result[1], 
                                result[2],
                                result[3],
                                str(user_id)
                            ])

                            text = f"Сообщение успешно запланировано на {result[0]}.{result[1]} {result[2]}:{result[3]}"
                            vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=modules.keyboards.kb_scheduled())
                        else:
                            text = "Не верный формат, попробуйте еще раз!"
                            vk.messages.send(user_id=user_id, random_id=0, message=text)

                    if event.obj.message["text"] == "Запланировать":
                        if process:
                            if process.poll() == 0 or process.poll() == 1:
                                state = "Запланировать"
                                text = "Теперь введите дату и время для планировки сообщения. В формате: DD.MM/HH:MM"
                                vk.messages.send(user_id=user_id, random_id=0, message=text)
                            else:
                                text = f"Сообщение успешно запланировано на {result[0]}.{result[1]} {result[2]}:{result[3]}"
                                vk.messages.send(user_id=user_id, random_id=0, message=text, keyboard=modules.keyboards.kb_scheduled())
                        else:
                            state = "Запланировать"
                            text = "Теперь введите дату и время для планировки сообщения. В формате: DD.MM/HH:MM"
                            vk.messages.send(user_id=user_id, random_id=0, message=text)
                    
                    if event.obj.message["text"] == "Отменить отправку":
                        process.kill()
                        vk.messages.send(user_id=user_id, random_id=0, message="Задача была отменена!")

                    if event.obj.message["text"] == "Разослать сообщение":
                        if process:
                            if process.poll() == 0 or process.poll() == 1:
                                modules.distribution_text(vk=vk, user_id=user_id)
                            else:
                                vk.messages.send(user_id=user_id, random_id=0, message="Для начала нужно отменить запланированую рассылку!")
                        else:
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
            continue


if __name__ == '__main__':
    modules.main_logger.info("Бот запущен!")
    main()
