import os


LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

POSTGRES_SYSTEM = 'postgresql'
POSTGRES_DRIVER = 'psycopg2'

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

POSTGRES_HOST_NAME = os.getenv('POSTGRES_HOST_NAME', 'db')