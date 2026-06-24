#!/usr/bin/env python3
"""
Скрипт для импорта пользователей из CSV-файлов, лежащих в подпапках data.
Каждая подпапка должна содержать:
    - один .env файл с переменной GROUP_ID=...
    - один .csv файл с колонками: user_id, first_name, last_name (без заголовков)
"""

import csv
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту, чтобы импортировать модел
from .models import User  # предполагается, что models.py лежит рядом со скриптом
from .config import connect_string


def get_db_session():
    """Создаёт сессию подключения к БД."""
    engine = create_engine(connect_string)
    Session = sessionmaker(bind=engine)
    return Session()


def read_env_file(env_path):
    """Извлекает GROUP_ID из .env файла без загрязнения глобального окружения."""
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('GROUP_ID='):
                value = line.split('=', 1)[1].strip()
                return int(value)
    raise ValueError(f"В файле {env_path} не найдена переменная GROUP_ID")


def find_csv_file(folder):
    """Возвращает первый CSV-файл в папке или None."""
    csv_files = list(folder.glob("*.csv"))
    return csv_files[0] if csv_files else None


def import_users_from_csv(csv_path, group_id, session):
    """
    Читает CSV и добавляет пользователей в БД.
    Пропускает уже существующих (user_id + group_id).
    Если колонок меньше 3, недостающие заменяются пустыми строками.
    """
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        added = 0
        skipped = 0

        for row in reader:
            if not row:
                continue

            # Приводим к трём колонкам, заполняя недостающие пустыми строками
            user_id_str = row[0].strip() if len(row) > 0 else ''
            first_name = row[1].strip() if len(row) > 1 else ''
            last_name = row[2].strip() if len(row) > 2 else ''

            if not user_id_str:
                continue

            try:
                user_id = int(user_id_str)
            except ValueError:
                print(f"  Пропускаем строку-заголовок (или нечисловое значение): {row}")
                continue

            # Проверяем дубликат
            exists = session.query(User).filter_by(
                user_id=user_id,
                group_id=group_id
            ).first()
            if exists:
                skipped += 1
                continue

            user = User(
                group_id=group_id,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            added += 1

        session.commit()
        print(f"  Добавлено: {added}, пропущено (дубликаты): {skipped}")


def main():
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir.parent / "data"

    if not data_dir.exists():
        print(f"Директория data не найдена: {data_dir}")
        return 1

    try:
        session = get_db_session()
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return 1

    for folder in data_dir.iterdir():
        if not folder.is_dir():
            continue

        print(f"\nОбработка папки: {folder.name}")

        env_file = folder / ".env"
        if not env_file.exists():
            print(f"  Пропуск: нет .env файла")
            continue

        try:
            group_id = read_env_file(env_file)
        except Exception as e:
            print(f"  Ошибка чтения .env: {e}")
            continue

        csv_file = find_csv_file(folder)
        if csv_file is None:
            print(f"  Пропуск: нет CSV-файла")
            continue

        print(f"  GROUP_ID = {group_id}, CSV = {csv_file.name}")
        try:
            import_users_from_csv(csv_file, group_id, session)
        except Exception as e:
            print(f"  Ошибка импорта: {e}")
            session.rollback()
            continue

    session.close()
    print("\nИмпорт завершён.")
    return 0


if __name__ == "__main__":
    sys.exit(main())