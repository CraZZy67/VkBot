import json
import logging
import time
from datetime import timezone, timedelta

from dotenv import load_dotenv
import os
import redis
from sqlalchemy import create_engine, select, Column, Integer, String, ForeignKey
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column
import vk_api


# local constants
MAX_SYMBOLS = 4096


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer(), unique=True)
    token: Mapped[str] = mapped_column(String(), unique=True)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    user_id: Mapped[int]
    first_name: Mapped[str]
    last_name: Mapped[str]


class Template(Base):
    __tablename__ = 'templates'
    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'), unique=True)
    subscribed: Mapped[str] = mapped_column(default='Default text sub')
    not_subscribed: Mapped[str] = mapped_column(default='Default text un_sub')
    distribution: Mapped[str] = mapped_column(default='Default text dist')


class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str]
    owner_id: Mapped[int]
    group_id: Mapped[int] = mapped_column(ForeignKey('groups.group_id', ondelete='CASCADE', onupdate='CASCADE'))
    run_at: Mapped[datetime]
    status: Mapped[str]


def make_engine_from_env():
    load_dotenv(override=True)
    db_system = os.getenv('DB_SYSTEM', 'postgresql')
    db_driver = os.getenv('DB_DRIVER', 'psycopg2')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    db_host = os.getenv('DB_HOST_NAME', 'db')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'postgres')
    connect_string = f"{db_system}+{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    echo = os.getenv('LOG_LEVEL', 'INFO').upper() == 'DEBUG'
    return create_engine(connect_string, echo=echo)


def make_session_factory():
    engine = make_engine_from_env()
    return sessionmaker(bind=engine)



def make_redis_from_env():
    load_dotenv(override=True)
    host = __import__('os').environ.get('REDIS_HOST', 'redis')
    port = int(__import__('os').environ.get('REDIS_PORT', '6379'))
    db = int(__import__('os').environ.get('REDIS_DB', '0'))
    password = __import__('os').environ.get('REDIS_PASSWORD', None)
    return redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)


def run_worker(queue_name='jobs_queue'):
    log = logging.getLogger('worker')
    redis_client = None

    try:
        redis_client = make_redis_from_env()
        redis_client.ping()
        log.info('Connected to Redis')
    except Exception:
        log.exception('Unable to connect to Redis')
        return

    # prepare DB session factory and initial group->api mapping
    Session = make_session_factory()
    groups_api = {}
    try:
        with Session() as s:
            rows = s.execute(select(Group.group_id, Group.token)).all()
            for gid, token in rows:
                try:
                    groups_api[gid] = vk_api.VkApi(token=token)
                except Exception:
                    log.exception('Failed to create VkApi for group %s', gid)
    except Exception:
        log.exception('Failed to load group APIs from DB')

    tz = timezone(timedelta(hours=3))

    while True:
        try:
            item = redis_client.blpop(queue_name, timeout=10)
            if not item:
                time.sleep(0.5)
                continue

            _, payload = item
            data = json.loads(payload)

            job_id = data.get('id')
            uuid = data.get('uuid')
            owner_id = data.get('owner_id')
            group_id = data.get('group_id')

            log.info('Picked job id=%s uuid=%s for group=%s', job_id, uuid, group_id)

            with Session() as session:
                # fetch job record
                job = session.execute(select(Job).where(Job.id == job_id)).scalars().one_or_none()
                if not job:
                    log.warning('Job id=%s not found in DB, skipping', job_id)
                    continue

                # mark processing
                try:
                    job.status = 'processing'
                    session.add(job)
                    session.commit()
                except Exception:
                    session.rollback()
                    log.exception('Failed to mark job processing id=%s', job_id)

                # ensure api for group (refresh from DB if needed)
                if group_id not in groups_api:
                    try:
                        row = session.execute(select(Group.group_id, Group.token).where(Group.group_id == group_id)).one_or_none()
                        if row:
                            _, token = row
                            groups_api[group_id] = vk_api.VkApi(token=token)
                    except Exception:
                        log.exception('Failed to refresh group api for group %s', group_id)

                api_obj = groups_api.get(group_id)
                if api_obj is None:
                    log.error('No Vk API for group=%s, marking job failed', group_id)
                    job.status = 'failed'
                    session.add(job)
                    session.commit()
                    continue

                vk = api_obj.get_api()

                # load distribution template
                template = session.execute(select(Template).where(Template.group_id == group_id)).scalars().one_or_none()
                if not template:
                    log.warning('No template for group=%s, skipping', group_id)
                    dist_text = ''
                else:
                    dist_text = getattr(template, 'distribution', '')

                # get users
                users = session.execute(select(User.user_id).where(User.group_id == group_id)).scalars().all()

                sent_count = 0
                for u in users:
                    try:
                        # split by MAX_SYMBOLS
                        parts = [dist_text[i:i+MAX_SYMBOLS] for i in range(0, len(dist_text), MAX_SYMBOLS)] or ['']
                        for part in parts:
                            vk.messages.send(user_id=u, random_id=0, message=part)
                        sent_count += 1
                    except Exception:
                        log.exception('Failed to send message to user=%s in group=%s', u, group_id)

                # finalize job
                try:
                    job.status = 'done'
                    session.add(job)
                    session.commit()
                except Exception:
                    session.rollback()
                    log.exception('Failed to mark job done id=%s', job_id)

                # notify owner
                try:
                    if owner_id and group_id in groups_api:
                        owner_vk = groups_api[group_id].get_api()
                        owner_vk.messages.send(
                            user_id=owner_id,
                            random_id=0,
                            message=f'Рассылка завершена для группы {group_id}. Отправлено: {sent_count} пользователей.'
                        )
                except Exception:
                    log.exception('Failed to notify owner=%s for job id=%s', owner_id, job_id)

        except Exception:
            log.exception('Unhandled exception in worker loop')
            time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    run_worker()
