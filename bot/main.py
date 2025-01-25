from aiogram.filters import Command
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio

from config import tg_bot_token


bot = Bot(token=tg_bot_token)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот, работающий на aiogram 3.x!")


# Основная точка входа
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())