import os
import json

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    orders = relationship("Order", back_populates="animal_class")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'), nullable=False)
    families = relationship("Family", back_populates="order")

    animal_class = relationship("Class", back_populates="orders")


class Family(Base):
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    genera = relationship("Genus", back_populates="family")

    order = relationship("Order", back_populates="families")


class Genus(Base):
    __tablename__ = 'genera'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    family_id = Column(Integer, ForeignKey('families.id'), nullable=False)
    species = relationship("Animal", back_populates="genus")

    family = relationship("Family", back_populates="genera")


class Animal(Base):
    __tablename__ = 'animals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True)
    genus_id = Column(Integer, ForeignKey('genera.id'), nullable=False)
    genus = relationship("Genus", back_populates="species")


load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("Переменная окружения DATABASE_URL не задана")

engine = create_engine(db_url)

# Создание таблиц
Base.metadata.create_all(engine)


SessionLocal = sessionmaker(bind=engine)

k = 0


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def add_data_to_db(data, session):
    global k
    required_keys = ['Класс', 'Отряд', 'Семейство', 'Род', 'URL изображения', 'Название животного']
    for item in data:
        try:
            # Заполняем пропущенные ключи значением "Неизвестно"
            for key in required_keys:
                if key not in item:
                    print(f"Ключ {key} отсутствует в записи, заменяем на 'Неизвестно'.")
                    item[key] = "Неизвестно"

            # Пропускаем животное "Большая панда, так как на него нельзя оформить опеку"
            if item['Название животного'] == 'Большая панда':
                continue

            # Используем session.no_autoflush для отключения автозаписи
            with session.no_autoflush:
                # Проверка и добавление класса
                animal_class = session.query(Class).filter_by(name=item['Класс']).first()
                if not animal_class and item['Класс'] != "Неизвестно":
                    animal_class = Class(name=item['Класс'])
                    session.add(animal_class)
                if item['Класс'] == "Неизвестно":
                    animal_class = session.query(Class).filter_by(name="Неизвестно").first()
                    if not animal_class:
                        animal_class = Class(name="Неизвестно")
                        session.add(animal_class)

                # Добавляем или получаем отряд
                order = session.query(Order).filter_by(name=item['Отряд'], class_id=animal_class.id).first()
                if not order and item['Отряд'] != "Неизвестно":
                    order = Order(name=item['Отряд'], animal_class=animal_class)
                    session.add(order)
                if item['Отряд'] == "Неизвестно":
                    order = session.query(Order).filter_by(name="Неизвестно", class_id=animal_class.id).first()
                    if not order:
                        order = Order(name="Неизвестно", animal_class=animal_class)
                        session.add(order)

                # Добавляем или получаем семейство
                family = session.query(Family).filter_by(name=item['Семейство'], order_id=order.id).first()
                if not family and item['Семейство'] != "Неизвестно":
                    family = Family(name=item['Семейство'], order=order)
                    session.add(family)
                if item['Семейство'] == "Неизвестно":
                    family = session.query(Family).filter_by(name="Неизвестно", order_id=order.id).first()
                    if not family:
                        family = Family(name="Неизвестно", order=order)
                        session.add(family)

                # Добавляем или получаем род
                genus = session.query(Genus).filter_by(name=item['Род'], family_id=family.id).first()
                if not genus and item['Род'] != "Неизвестно":
                    genus = Genus(name=item['Род'], family=family)
                    session.add(genus)
                    session.commit()  # Здесь важно сохранить объект, чтобы он получил id
                if item['Род'] == "Неизвестно":
                    genus = session.query(Genus).filter_by(name="Неизвестно", family_id=family.id).first()
                    if not genus:
                        genus = Genus(name="Неизвестно", family=family)
                        session.add(genus)
                        session.commit()  # Сохраняем, чтобы получить id

                # Теперь добавляем животное с правильно заданным genus_id
                animal = session.query(Animal).filter_by(name=item['Название животного'], genus=genus).first()
                if not animal:
                    animal = Animal(
                        name=item['Название животного'],
                        image_url=item['URL изображения'],
                        genus=genus  # здесь обязательно указываем уже сохраненный род
                    )
                    session.add(animal)

        except Exception as e:
            session.rollback()
            k=k+1
            print(f"Ошибка при обработке записи: {item}, ошибка: {e}")

    session.commit()


# Основной блок программы
if __name__ == "__main__":
    # Загружаем данные из JSON
    json_file = r"C:\Users\Maria\PycharmProjects\MoscowZooBot\bot\services\animals_classification.json"
    json_data = load_json(json_file)

    # Подключаемся к базе данных и добавляем данные
    with SessionLocal() as session:
        add_data_to_db(json_data, session)
    print('k=', k)
    print("Данные успешно добавлены в базу данных!")
