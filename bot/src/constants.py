import os


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

DB_SYSTEM = 'postgresql'
DB_DRIVER = 'psycopg2'

DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

EVENT_WAIT = os.getenv('EVENT_WAIT', 10)

DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

DB_HOST_NAME = os.getenv('POSTGRES_HOST_NAME', 'db')

MAX_SYMBOLS = 4096