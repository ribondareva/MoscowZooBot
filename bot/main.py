from bot.services.parser import parse_and_collect_data
from bot.utils.db import SessionLocal, add_data_to_db, ensure_unknown_entries


def parse_data():
    data = parse_and_collect_data()
    if not data:  # Проверяем, что данные получены
        print("Ошибка: данные не были получены, процесс остановлен.")
        return
    with SessionLocal() as session:
        ensure_unknown_entries(session)
        add_data_to_db(data, session)
    print("Данные успешно добавлены в базу!")


if __name__ == "__main__":
    parse_data()









# #
# @dp.message(Command("start"))
# async def start_handler(message: Message):
#     await message.answer("Привет! Я бот, работающий на aiogram 3.x!")
#
#
#
# async def main():
#     print("Бот запускается...")
#     await dp.start_polling(bot)


# if __name__ == "__main__":
#     asyncio.run(main())
