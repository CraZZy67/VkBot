from enum import Enum, StrEnum, auto

class CommandsEn(Enum):
    USERS = '/users'
    PLANE_DIST = 'Запланировать рассылку'
    DIST_NOW = 'Разослать сейчас'
    CANCEL_DIST = 'Отменить рассылку',
    CHANGE = '/change'

class StatesEn(StrEnum):
    PLANE_DIST = auto()
    CHANGE = auto()
    CANCEL = auto()

class StatusesEn(StrEnum):
    PENDING = auto()
    CANCEL = auto()

class CheckWordsEn(StrEnum):
    BEGIN = 'Начать'
    BEGIN_ENG = 'Start'
    SUBSCRIBED = 'Подписался'

class TemplateNames(StrEnum):
    SUBSCRIBE = 'follow'
    NOT_SUBSCRIBE = 'un_follow'
    DISTRIBUTION = 'distribution'