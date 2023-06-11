import logging
import os
import sys
from logging import config as logging_config
from typing import Any

from pydantic import BaseSettings, PostgresDsn, validator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append('src')


class AppSettings(BaseSettings):
    LOG_LEVEL = 'INFO'

    APP_TITLE: str
    PROJECT_HOST: str
    PROJECT_PORT: int

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    MAX_FILE_SIZE: int = 1024 * 1024 * 10
    SECRET: str
    TOKEN_EXPIRE: int = 60 * 60

    DATABASE_URL: str = ''

    FILE_FOLDER: str = 'files/'

    @validator('DATABASE_URL', pre=True, check_fields=False)
    def assemble_db_connection(cls, value: str | None, values: dict[str, Any]) -> Any:
        if isinstance(value, str) and value != '':
            return value
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_HOST'),
            port=str(values.get('POSTGRES_PORT')),
            path=f'/{values.get("POSTGRES_DB") or ""}',
        )

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
