import os
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv

from pydantic import BaseSettings

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')

    server_host: str
    server_port: int

    database_url: str = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

    jwt_secret: str = os.environ.get('JWT_SECRET')
    jwt_algorithm: str = 'HS256'
    jwt_expiration: int = 3600 * 20


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
