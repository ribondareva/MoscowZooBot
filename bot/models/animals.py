from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


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
