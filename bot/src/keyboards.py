from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from .enums import CommandsEn, CheckWordsEn, TemplateNamesEn


def kb_not_subscribed():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.POSITIVE, label=CheckWordsEn.SUBSCRIBED)

    return kb.get_keyboard()

def kb_users():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=CommandsEn.PLANE_DIST.value)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=CommandsEn.DIST_NOW.value)
    kb.add_button(color=VkKeyboardColor.NEGATIVE, label=CommandsEn.CANCEL_DIST.value)
    

    return kb.get_keyboard()

def kb_templates():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=TemplateNamesEn.SUBSCRIBE)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=TemplateNamesEn.NOT_SUBSCRIBE)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=TemplateNamesEn.DISTRIBUTION)

    return kb.get_keyboard()