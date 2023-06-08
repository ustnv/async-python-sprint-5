import logging
import os
import sys
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append('src')

class AppSettings(BaseSettings):
    LOG_LEVEL = 'INFO'

    APP_TITLE: str
    PROJECT_HOST: str
    PROJECT_PORT: int

    DATABASE_URL: PostgresDsn

    TEST_DB_NAME = 'aps5_test_db'

    FILE_FOLDER: str = 'files/'

    class Config:
        env_file = os.path.dirname(BASE_DIR) + '/.env'


settings = AppSettings()

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': settings.LOG_LEVEL,
        },
    },
}

logging_config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
