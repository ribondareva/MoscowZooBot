# Загрузка конфигурации
from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    api_url: str
    debug: bool = False  # Значение по умолчанию, если переменной нет в .env


class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"


config = Settings()
