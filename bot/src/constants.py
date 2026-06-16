from dotenv import load_dotenv

import os


load_dotenv(override=True)

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

DB_SYSTEM = 'postgresql'
DB_DRIVER = 'psycopg2'

DB_USER = os.getenv('DB_USER', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

EVENT_WAIT = os.getenv('EVENT_WAIT', 10)

DB_PASSWORD = os.getenv('DB_PASSWORD')

DB_HOST_NAME = os.getenv('DB_HOST_NAME', 'db')

MAX_SYMBOLS = 4096