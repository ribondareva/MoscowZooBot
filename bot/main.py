# Точка входа в бота
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.services.parser import parse_and_collect_data
from bot.utils.db import (
    async_session_maker,
    add_data_to_db,
    create_feedback_table,
    create_user_table,
    create_all_tables,
)
from bot.handlers.start_quiz import router as start_router
from bot.handlers.end_quiz import router as end_router
from bot.handlers.quiz import router as quiz_router
from bot.handlers.contacts import router as contacts_router
from bot.handlers.feedback import router as feedback_router
from bot.handlers.share import router as share_router
from bot.utils.config import config
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession


BOT_TOKEN = config.bot_token
if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN в переменных окружения!")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Middleware для передачи db_session
async def db_session_middleware(handler, event, data):
    async with async_session_maker() as session:
        data["db_session"] = session
        return await handler(event, data)


dp.update.middleware(db_session_middleware)

# Подключаем роутеры
dp.include_router(start_router)  # Роутер из start_quiz.py
dp.include_router(end_router)  # Роутер из end_quiz.py
dp.include_router(quiz_router)  # Роутер из quiz.py
dp.include_router(contacts_router)  # Роутер из contacts.py
dp.include_router(feedback_router)  # Роутер из feedback.py
dp.include_router(share_router)  # Роутер из share.py


# Парсинг данных и добавление в базу
async def parse_data():
    data = parse_and_collect_data()
    if not data:
        print("Ошибка: данные не были получены, процесс остановлен.")
        return
    async with async_session_maker() as session:
        await add_data_to_db(data, session)
    print("Данные успешно добавлены в базу!")


async def table_exists(session: AsyncSession, table_name: str):
    """Проверяет, существует ли таблица в базе данных."""
    return await session.run_sync(
        lambda sync_session: inspect(sync_session.bind).has_table(table_name)
    )


# Основная функция запуска
async def main():
    await bot.set_my_commands(
        [BotCommand(command="contacts", description="Связаться с нами")]
    )
    # Проверка и создание таблиц, если они не существуют
    print("Проверка и создание таблиц...")
    async with async_session_maker() as session:
        if not await table_exists(session, "users"):
            await create_user_table()

        if not await table_exists(session, "feedbacks"):
            await create_feedback_table()

        if not await table_exists(session, "animals"):
            await create_all_tables()
        else:
            # Проверяем, пуста ли таблица animals
            result = await session.execute(text("SELECT COUNT(*) FROM animals"))
            count = result.scalar()  # Получаем количество записей
            if count == 0:
                # Если таблица пуста, добавляем данные
                print("Таблица animals пуста, добавляем данные...")
                await parse_data()
            else:
                print("Таблица animals уже содержит данные.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
