from vk_api.keyboard import VkKeyboard, VkKeyboardColor


buttons = ["follow.txt", "un_follow.txt", "distribution.txt"]


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
    kb.add_button(color=VkKeyboardColor.POSITIVE, label="follow.txt")
    kb.add_button(color=VkKeyboardColor.NEGATIVE, label="un_follow.txt")
    kb.add_button(color=VkKeyboardColor.PRIMARY, label="distribution.txt")

    return kb.get_keyboard()
