import requests
import vk_api
from vk_api.vk_api import VkApiMethod

from logger import main_logger


def handling_docs(vk: VkApiMethod, attachment, state: str) -> str:
    file_type = attachment['doc']['ext']
    file_url = attachment['doc']['url']
    file_name = attachment['doc']['title']

    try:
        main_logger.info(f"Получен файл: {file_name} ({file_type})")
        main_logger.info(f"Ссылка для загрузки: {file_url}")

        get_file(file_url, file_name, state)

    except vk_api.exceptions.ApiError as ex:
        main_logger.error(f"Ошибка при получении файла: {ex}")
    except requests.exceptions.RequestException as ex:
        main_logger.error(f"Ошибка при скачивании файла: {ex}")

    clear = ""
    return clear


def get_file(file_url, file_name, state: str) -> None:
    response = requests.get(file_url, stream=True)
    response.encoding = "utf-8"
    response.raise_for_status()

    with open(f"texts/{state}", 'w', encoding="utf-8") as f:
        f.write(response.text)

    main_logger.info(f"Файл {file_name} сохранен в рабочую директорию.")
