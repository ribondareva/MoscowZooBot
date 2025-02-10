# Загрузка конфигурации
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings  # type: ignore


ENV_FILE = ".test.env" if os.getenv("TEST_ENV", "false") == "true" else ".env"
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    api_url: str
    support_chat_id: int
    debug: bool = False  # Значение по умолчанию, если переменной нет в .env

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"


config = Settings()
