from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from .config import CommandsEn
from .enums import CheckWordsEn

def kb_not_subscribed():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.POSITIVE, label=CheckWordsEn.SUBSCRIBED)

    return kb.get_keyboard()

def kb_users():
    kb = VkKeyboard(one_time=False, inline=True)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=CommandsEn.PLANE_DIST)
    kb.add_button(color=VkKeyboardColor.PRIMARY, label=CommandsEn.DIST_NOW)
    kb.add_button(color=VkKeyboardColor.NEGATIVE, label=CommandsEn.CANCEL_DIST)

    return kb.get_keyboard()