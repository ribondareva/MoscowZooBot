import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from bot.services.parser import parse_and_collect_data
from bot.utils.db import SessionLocal, add_data_to_db
from bot.handlers.start_quiz import start_quiz
import asyncio


BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN в переменных окружения!")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Роутер для обработки сообщений
router = Router()


# Обработка команды /start
@router.message(F.text.casefold() == "/start")
async def start(message: Message, state: FSMContext):
    with SessionLocal() as session:  # Создаем сессию базы данных
        await start_quiz(message, state, session)


# Парсинг данных и добавление в базу
def parse_data():
    data = parse_and_collect_data()
    if not data:
        print("Ошибка: данные не были получены, процесс остановлен.")
        return
    with SessionLocal() as session:
        # ensure_unknown_entries(session)
        add_data_to_db(data, session)
    print("Данные успешно добавлены в базу!")


# Основная функция запуска
async def main():
    dp.include_router(router)  # Подключаем роутер
    await bot.delete_webhook(drop_pending_updates=True)  # Очищаем старые обновления
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Раскомментируйте, чтобы запустить парсинг и добавление данных в базу
    # parse_data()

    asyncio.run(main())
