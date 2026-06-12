from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def kb_not_subscribed():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.POSITIVE, label='Подписался')

    return kb.get_keyboard()