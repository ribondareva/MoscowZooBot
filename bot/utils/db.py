from dotenv import load_dotenv
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from bot.models.feedback import Feedback
from bot.utils.config import config
from bot.models.animals import Class, Order, Family, Genus, Animal, Base
from bot.models.user import User


# Загрузка переменных окружения
load_dotenv()

# Получаем URL базы данных из конфигурации
db_url = config.database_url
if not db_url:
    raise ValueError("Переменная окружения DATABASE_URL не задана")

# Используем асинхронный движок
engine = create_async_engine(db_url, echo=True)

# Создаем асинхронную фабрику сессий
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_all_tables():
    """Создает все таблицы в базе данных (асинхронно)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Все таблицы были успешно созданы.")


async def create_user_table():
    """Создает только таблицу для пользователей (асинхронно)."""
    async with engine.begin() as conn:
        await conn.run_sync(User.__table__.create)
    print("Таблица пользователей была успешно создана.")


async def create_feedback_table():
    """Создает только таблицу для отзывов (асинхронно)."""
    async with engine.begin() as conn:
        await conn.run_sync(Feedback.__table__.create)
    print("Таблица отзывов была успешно создана.")


async def save_user_to_db(
    chat_id, username, is_active=True, user_state="unknown", chosen_animal="not chosen"
):
    """Сохраняет информацию о пользователе в базу данных асинхронно."""

    async with async_session_maker() as session:
        async with session.begin():  # Блокируем транзакцию для выполнения изменений
            # Проверяем, существует ли пользователь с таким chat_id
            result = await session.execute(select(User).filter_by(chat_id=chat_id))
            user = result.scalars().first()

            if user:
                # Если пользователь существует, обновляем его данные
                user.username = username
                user.is_active = is_active
                user.state = user_state
                user.chosen_animal = chosen_animal
                print(f"Пользователь {username} обновлен в базе данных.")
            else:
                # Если пользователь не существует, создаем нового
                user = User(
                    chat_id=chat_id,
                    username=username,
                    is_active=is_active,
                    state=user_state,
                    chosen_animal=chosen_animal,
                )
                session.add(user)
                print(f"Пользователь {username} успешно сохранен в базу данных.")

            await session.commit()


def get_or_create(session, model, **kwargs):
    """Получает или создает запись в базе данных, если она не существует."""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False  # Если запись существует
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()  # Фиксируем изменения, чтобы получить ID
        return instance, True  # Если запись не найдена и создаем новую


def add_order_with_on_conflict(session, name, class_id):
    """Добавляет отряд, если он ещё не существует (с учетом уникальности)."""
    session.execute(
        text(
            "INSERT INTO orders (name, class_id) VALUES (:name, :class_id) ON CONFLICT (name) DO NOTHING"
        ),
        {"name": name, "class_id": class_id},
    )


def add_family_with_on_conflict(session, name, order_id):
    """Добавляет семейство, если оно ещё не существует (с учетом уникальности)."""
    session.execute(
        text(
            "INSERT INTO families (name, order_id) VALUES (:name, :order_id) ON CONFLICT (name, order_id) DO NOTHING"
        ),
        {"name": name, "order_id": order_id},
    )


async def add_data_to_db(data, session):
    """Добавляет животных в базу данных, исключая тех, у кого отсутствует классификация."""
    await create_all_tables()
    required_keys = [
        "Класс",
        "Отряд",
        "Семейство",
        "Род",
        "URL изображения",
        "Название животного",
    ]

    for item in data:
        try:
            # Проверяем, есть ли все ключи и они не пустые
            if any(key not in item or not item[key].strip() for key in required_keys):
                print(
                    f"Пропускаем {item.get('Название животного', 'Без названия')} — неполная классификация."
                )
                continue

            # Пропускаем "Большую панду"
            if item["Название животного"] == "Большая панда":
                continue

            # Начинаем транзакцию
            async with session.begin():
                # Получаем или создаем класс
                animal_class, _ = get_or_create(session, Class, name=item["Класс"])

                # Проверяем, что класс был создан или найден
                if not animal_class:
                    raise ValueError(
                        f"Класс '{item['Класс']}' не был создан или найден."
                    )

                # Добавляем отряд с проверкой уникальности
                add_order_with_on_conflict(session, item["Отряд"], animal_class.id)
                order = (
                    session.query(Order)
                    .filter_by(name=item["Отряд"], class_id=animal_class.id)
                    .first()
                )

                # Проверяем, что отряд был создан или найден
                if not order:
                    raise ValueError(
                        f"Отряд '{item['Отряд']}' не был создан или найден."
                    )

                # Добавляем семейство с проверкой уникальности
                add_family_with_on_conflict(session, item["Семейство"], order.id)
                family = (
                    session.query(Family)
                    .filter_by(name=item["Семейство"], order_id=order.id)
                    .first()
                )

                # Проверяем, что семейство было создано или найдено
                if not family:
                    raise ValueError(
                        f"Семейство '{item['Семейство']}' не было создано или найдено."
                    )

                # Получаем или создаем род
                genus, _ = get_or_create(
                    session, Genus, name=item["Род"], family_id=family.id
                )

                # Проверяем существование животного
                animal = (
                    session.query(Animal)
                    .filter_by(name=item["Название животного"])
                    .first()
                )
                if not animal:
                    animal = Animal(
                        name=item["Название животного"],
                        image_url=item["URL изображения"],
                        genus=genus,
                    )
                    session.add(animal)

        except Exception as e:
            # В случае ошибки транзакция откатывается автоматически
            print(
                f"Ошибка при обработке записи {item.get('Название животного', 'Без названия')}: {e}"
            )
