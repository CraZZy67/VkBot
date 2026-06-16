import os
import time
import json
import signal
import logging
from datetime import datetime, timezone, timedelta
from threading import Event
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, String, DateTime, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import redis


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    owner_id = Column(Integer)
    group_id = Column(Integer)
    run_at = Column(DateTime)
    status = Column(String)


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


def make_redis_from_env():
    load_dotenv(override=True)

    host = os.getenv('REDIS_HOST', 'redis')
    port = int(os.getenv('REDIS_PORT', '6379'))
    db = int(os.getenv('REDIS_DB', '0'))
    password = os.getenv('REDIS_PASSWORD', None)
    return redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)


def configure_logging():
    level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(message)s')
    return logging.getLogger('scheduler')


STOP = Event()


def handle_signal(signum, frame):
    STOP.set()


def validate_and_send(session, redis_client, logger, queue_name='jobs_queue'):
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)

    # 1) Remove canceled jobs
    try:
        canceled = session.execute(select(Job).where(Job.status == 'cancel')).scalars().all()
        if canceled:
            logger.info('Removing %d canceled jobs', len(canceled))
            for j in canceled:
                session.delete(j)
            session.commit()
    except Exception:
        logger.exception('Failed to remove canceled jobs')
        session.rollback()

    # 1.b) Remove finished jobs (processed by worker)
    try:
        finished = session.execute(select(Job).where(Job.status == 'done')).scalars().all()
        if finished:
            logger.info('Removing %d finished jobs', len(finished))
            for j in finished:
                session.delete(j)
            session.commit()
    except Exception:
        logger.exception('Failed to remove finished jobs')
        session.rollback()

    # 2) Find jobs that should run now or earlier
    try:
        rows = session.execute(select(Job).where(Job.run_at <= now).order_by(Job.group_id, Job.run_at, Job.id)).scalars().all()
    except Exception:
        logger.exception('Failed to query ready jobs')
        session.rollback()
        return

    if not rows:
        return

    # 3) Deduplicate exact duplicates by (group_id, run_at) and
    #    skip jobs in the same group if the difference to the
    #    previously scheduled/sent job is less than 1 hour.
    seen = set()
    to_send = []
    to_delete = []

    last_sent_per_group: dict[int, datetime] = {}

    for job in rows:
        # normalize job.run_at to scheduler timezone
        job_run = job.run_at
        try:
            if job_run is None:
                # defensive: skip malformed rows
                logger.warning('Job id=%s has no run_at, skipping', getattr(job, 'id', None))
                continue

            if job_run.tzinfo is None:
                job_run = job_run.replace(tzinfo=tz)
            else:
                job_run = job_run.astimezone(tz)
        except Exception:
            logger.exception('Failed to normalize run_at for job id=%s', getattr(job, 'id', None))
            continue

        key = (job.group_id, job_run)
        if key in seen:
            to_delete.append(job)
            continue

        seen.add(key)

        # enforce minimum 1 hour gap per group: skip job if previous sent
        # job in same group is less than 1 hour before this job
        prev = last_sent_per_group.get(job.group_id)
        if prev is not None and (job_run - prev) < timedelta(hours=1):
            logger.info('Skipping job id=%s in group=%s: previous at %s (less than 1h)', job.id, job.group_id, prev.isoformat())
            # do not delete the row; it remains in DB for future consideration
            continue

        # mark this job as the last sent time for its group
        last_sent_per_group[job.group_id] = job_run
        # store normalized run_at back to job for payload
        job._normalized_run_at = job_run
        to_send.append(job)

    if to_delete:
        logger.info('Removing %d duplicate jobs (same group/run_at)', len(to_delete))
        try:
            for j in to_delete:
                session.delete(j)
            session.commit()
        except Exception:
            logger.exception('Failed to delete duplicate jobs')
            session.rollback()

    # 4) Push to Redis and mark as sent
    for job in to_send:
        try:
            if job.status and job.status.lower() in ('sent', 'processing'):
                logger.debug('Skipping job %s, status=%s', job.id, job.status)
                continue

            run_at_val = getattr(job, '_normalized_run_at', job.run_at)
            payload = {
                'id': job.id,
                'uuid': job.uuid,
                'owner_id': job.owner_id,
                'group_id': job.group_id,
                'run_at': run_at_val.isoformat()
            }

            redis_client.rpush(queue_name, json.dumps(payload))
            job.status = 'sent'
            session.add(job)
            session.commit()
            logger.info('Dispatched job id=%s uuid=%s to redis', job.id, job.uuid)
        except Exception:
            logger.exception('Failed to dispatch job id=%s', getattr(job, 'id', None))
            session.rollback()


def main():
    configure_logging()
    logger = logging.getLogger('scheduler')

    engine = make_engine_from_env()
    Session = sessionmaker(bind=engine)

    redis_client = None
    try:
        redis_client = make_redis_from_env()
        # quick ping
        redis_client.ping()
    except Exception:
        logger.exception('Unable to connect to Redis on start')
        # will try later in loop
        redis_client = None

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    interval = int(os.getenv('SCHEDULER_INTERVAL', '30'))

    logger.info('Scheduler started, checking every %s seconds', interval)

    while not STOP.is_set():
        try:
            if redis_client is None:
                try:
                    redis_client = make_redis_from_env()
                    redis_client.ping()
                    logger.info('Connected to Redis')
                except Exception:
                    logger.exception('Redis still unavailable')

            with Session() as session:
                validate_and_send(session, redis_client or make_redis_from_env(), logger)

        except Exception:
            logger.exception('Unhandled error in scheduler main loop')

        # Wait with ability to break early
        for _ in range(interval):
            if STOP.is_set():
                break
            time.sleep(1)

    logger.info('Scheduler stopping')


if __name__ == '__main__':
    main()
