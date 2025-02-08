from bot.utils.db import Class, Order, Family, Genus, Animal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_classes(session: AsyncSession):
    result = await session.execute(select(Class))
    return result.scalars().all()


async def get_orders(session: AsyncSession, class_id):
    result = await session.execute(select(Order).filter_by(class_id=class_id))
    return result.scalars().all()


async def get_families(session: AsyncSession, order_id):
    result = await session.execute(select(Family).filter_by(order_id=order_id))
    return result.scalars().all()


async def get_genera(session: AsyncSession, family_id):
    result = await session.execute(select(Genus).filter_by(family_id=family_id))
    return result.scalars().all()


async def get_animals(session: AsyncSession, genus_id):
    result = await session.execute(select(Animal).filter_by(genus_id=genus_id))
    return result.scalars().all()


async def get_class_by_name(session: AsyncSession, name):
    result = await session.execute(select(Class).filter_by(name=name))
    return result.scalars().first()


async def get_orders_by_class_name(session: AsyncSession, class_name):
    # Сначала получаем класс по имени
    animal_class = await get_class_by_name(session, class_name)
    if not animal_class:
        return []  # Если класс не найден, возвращаем пустой список

    # Теперь используем id класса для получения отрядов
    result = await session.execute(select(Order).filter_by(class_id=animal_class.id))
    return result.scalars().all()
