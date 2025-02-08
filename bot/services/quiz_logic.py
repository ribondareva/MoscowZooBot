from bot.utils.db import Class, Order, Family, Genus, Animal


def get_classes(session):
    return session.query(Class).all()


def get_orders(session, class_id):
    return session.query(Order).filter_by(class_id=class_id).all()


def get_families(session, order_id):
    return session.query(Family).filter_by(order_id=order_id).all()


def get_genera(session, family_id):
    return session.query(Genus).filter_by(family_id=family_id).all()


def get_animals(session, genus_id):
    return session.query(Animal).filter_by(genus_id=genus_id).all()


def get_class_by_name(session, name):
    return session.query(Class).filter_by(name=name).first()


def get_orders_by_class_name(session, class_name):
    # Сначала получаем класс по имени
    animal_class = get_class_by_name(session, class_name)
    if not animal_class:
        return []  # Если класс не найден, возвращаем пустой список

    # Теперь используем id класса для получения отрядов
    return session.query(Order).filter_by(class_id=animal_class.id).all()
