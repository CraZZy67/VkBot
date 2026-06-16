from enum import Enum, StrEnum, auto

class CommandsEn(Enum):
    USERS = '/users'
    PLANE_DIST = 'Запланировать'
    DIST_NOW = 'Разослать'
    CANCEL_DIST = 'Отменить'
    CHANGE = '/change'
    CLEAR = '/clear'

class StatesEn(StrEnum):
    PLANE_DIST = auto()
    CHANGE = auto()
    CANCEL = auto()

class CheckWordsEn(StrEnum):
    BEGIN = 'Начать'
    BEGIN_ENG = 'Start'
    SUBSCRIBED = 'Подписался'

class TemplateNamesEn(StrEnum):
    SUBSCRIBE = 'follow'
    NOT_SUBSCRIBE = 'un_follow'
    DISTRIBUTION = 'distribution'

class JobStatusesEn(StrEnum):
    PENDING = auto()
    QUEUE = auto()
    PROCESS = auto()
    DONE = auto()
    CANCEL = auto()