import os.path
from pathlib import Path
from typing import Literal, Union

import toml
import tempfile
from pydantic import AnyHttpUrl, AnyUrl, BaseSettings, validator

PROJECT_DIR = os.path.abspath(Path(__file__).parent.parent.parent)
PYPROJECT_CONTENT = toml.load(f'{PROJECT_DIR}/pyproject.toml')['tool']['poetry']


class Settings(BaseSettings):
    class Config:
        env_file = os.path.join(PROJECT_DIR, '.env')
        case_sensitive = True

    ENVIRONMENT: Literal["DEV", "PYTEST", "PRODUCTION"]
    BACKEND_CORS_ORIGINS: Union[str, list[AnyHttpUrl]]

    PROJECT_NAME: str = PYPROJECT_CONTENT['name']
    VERSION: str = PYPROJECT_CONTENT['version']
    DESCRIPTION: str = PYPROJECT_CONTENT['description']

    STORAGE_DIR: str = os.path.join(PROJECT_DIR, '.storage')
    THUMBNAILS_DIR: str = os.path.join(PROJECT_DIR, '.thumbnails')
    TEMP_DIR: str = tempfile.mkdtemp(prefix="image-storage-compared-")

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = '5432'
    AUTORUN_MIGRATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = ''

    @validator('SQLALCHEMY_DATABASE_URI')
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:  # noqa
        return AnyUrl.build(
            scheme='postgresql+asyncpg',
            user=values.get('POSTGRES_USER'),
            password=values.get('POSTGRES_PASSWORD'),
            host=values.get('POSTGRES_SERVER'),
            port=values.get('POSTGRES_PORT'),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    @validator('STORAGE_DIR')
    def _assemble_storage(cls, v: str, values: dict[str, str]) -> str:  # noqa
        path = os.path.abspath(v)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


settings = Settings()
