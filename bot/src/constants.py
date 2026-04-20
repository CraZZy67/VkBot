import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

DB_SYSTEM = 'postgresql'
DB_DRIVER = 'psycopg2'

DB_USER = os.getenv('DB_USER', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

DB_PASSWORD = os.getenv('DB_PASSWORD')

DB_HOST_NAME = os.getenv('DB_HOST_NAME', 'db')