from enum import StrEnum, auto


class JobStatusesEn(StrEnum):
    PENDING = auto()
    QUEUE = auto()
    PROCESS = auto()
    DONE = auto()
    CANCEL = auto()