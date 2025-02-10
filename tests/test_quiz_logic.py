import os
import pytest
from sqlalchemy import text
from bot.utils.db import async_session_maker, create_all_tables, create_user_table
from bot.models.user import User
from sqlalchemy.future import select


# Устанавливаем TEST_ENV=true перед тестами
os.environ["TEST_ENV"] = "true"


@pytest.fixture(scope="function")
async def clear_db():
    """Фикстура для очистки базы данных перед каждым тестом."""
    async with async_session_maker() as session:
        async with session.begin():
            await session.execute(text("DROP TABLE IF EXISTS users CASCADE;"))

    # Создание таблиц заново
    await create_user_table()


@pytest.mark.asyncio
async def test_save_user_to_db(clear_db):
    """Тест на создание пользователя в in-memory базе данных."""

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
