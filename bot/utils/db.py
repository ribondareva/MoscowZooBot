# модели и работа с базой
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import text
from bot.utils.config import config


Base = declarative_base()


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    orders = relationship("Order", back_populates="animal_class")

    # Добавляем уникальное ограничение для столбца name
    __table_args__ = (UniqueConstraint("name", name="uq_class_name"),)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    families = relationship("Family", back_populates="order")
    animal_class = relationship("Class", back_populates="orders")

    # Добавляем уникальное ограничение для столбца name
    __table_args__ = (UniqueConstraint("name", name="uq_order_name"),)


class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    genera = relationship("Genus", back_populates="family")

    order = relationship("Order", back_populates="families")

    # Добавляем уникальное ограничение для (name, order_id)
    __table_args__ = (
        UniqueConstraint("name", "order_id", name="uq_family_name_order_id"),
    )


class Genus(Base):
    __tablename__ = "genera"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    species = relationship("Animal", back_populates="genus")

    family = relationship("Family", back_populates="genera")

    # Добавляем уникальное ограничение для (name, family_id)
    __table_args__ = (
        UniqueConstraint("name", "family_id", name="uq_genus_name_family_id"),
    )


class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    genus_id = Column(Integer, ForeignKey("genera.id"), nullable=False)
    genus = relationship("Genus", back_populates="species")

    # Добавляем уникальное ограничение для (name, genus_id)
    __table_args__ = (
        UniqueConstraint("name", "genus_id", name="uq_animal_name_genus_id"),
    )


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
