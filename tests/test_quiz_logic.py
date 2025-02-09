# Юнит-тесты для логики викторины
import pytest
from dotenv import load_dotenv

from bot.utils.db import async_session_maker, create_all_tables, create_user_table
from bot.models.user import User
from sqlalchemy.future import select


load_dotenv()


@pytest.mark.asyncio
async def test_create_user_in_memory_db():
    """Тест на создание пользователя в in-memory базе данных."""

    # Создаём таблицы в in-memory базе данных
    async with async_session_maker() as session:
        async with session.begin():
            await create_all_tables()
            await create_user_table()

    # Добавляем тестового пользователя
    async with async_session_maker() as session:
        async with session.begin():
            new_user = User(
                chat_id=12345,
                username="test_user",
                is_active=True,
                state="test_state",
                chosen_animal="test_animal",
            )
            session.add(new_user)

    # Проверяем, что пользователь добавился
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.chat_id == 12345))
        user = result.scalars().first()

    assert user is not None, "Пользователь не найден в базе"
    assert user.username == "test_user", "Имя пользователя не совпадает"
    assert user.state == "test_state", "Состояние пользователя не совпадает"
