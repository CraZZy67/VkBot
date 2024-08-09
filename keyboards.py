from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def kb_un_follow():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.POSITIVE, label="Я подписался")

    return kb.get_keyboard()


def kb_db_info():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.NEGATIVE, label="Отчистить базу данных")
    kb.add_button(color=VkKeyboardColor.POSITIVE, label="Разослать сообщение")

    return kb.get_keyboard()


def kb_texts():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.POSITIVE, label="Подписан")
    kb.add_button(color=VkKeyboardColor.NEGATIVE, label="Не подписан")
    kb.add_button(color=VkKeyboardColor.PRIMARY, label="Рассылка")

    return kb.get_keyboard()
