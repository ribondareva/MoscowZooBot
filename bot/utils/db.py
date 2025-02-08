# модели и работа с базой
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from bot.utils.config import config
from bot.models.animals import Class, Order, Family, Genus, Animal, Base


load_dotenv()
db_url = config.database_url
if not db_url:
    raise ValueError("Переменная окружения DATABASE_URL не задана")

engine = create_engine(db_url)
# Создание таблиц
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


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


def add_data_to_db(data, session):
    """Добавляет животных в базу данных, исключая тех, у кого отсутствует классификация."""
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
            with session.begin():
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

                # Все операции завершены, транзакция зафиксируется автоматически при выходе из блока `with`

        except Exception as e:
            # В случае ошибки транзакция откатывается автоматически
            print(
                f"Ошибка при обработке записи {item.get('Название животного', 'Без названия')}: {e}"
            )
