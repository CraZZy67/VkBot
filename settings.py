from dotenv import load_dotenv

from dataclasses import dataclass
import os

load_dotenv()


@dataclass(frozen=True, init=False)
class Settings:
    TOKEN: str = os.getenv("TOKEN")
    GROUP_ID: str = os.getenv("GROUP_ID")
    ADMINS: str = os.getenv("ADMINS")

    WORDS = (
            "начать", "start", "/start", "/начать", "Начать", "Start",
            "Я подписался!", "я подписался", "Я подписался", "я подписался!"
    )

    PATH_DB = "data/users_db.csv"
    PATH_DISTRIBUTION = "texts/distribution.txt"
    PATH_FOLLOW = "texts/follow.txt"
    PATH_UN_FOLLOW = "texts/un_follow.txt"


settings = Settings()
