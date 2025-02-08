from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from bot.services.quiz_logic import get_class_by_name
from bot.handlers.states import QuizState
from bot.models.animals import Order, Family, Genus, Animal
from bot.utils.db import save_user_to_db

router = Router()


@router.message(QuizState.choose_class)
async def process_class_selection(message: Message, state: FSMContext, db_session):
    chat_id = message.from_user.id
    username = message.from_user.username or "unknown"
    is_active = True
    state_str = await state.get_state()
    chosen_animal = "not chosen"
    await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)
    class_name = message.text.strip()
    # Получаем класс по имени
    animal_class = get_class_by_name(db_session, class_name)

    if not animal_class:
        await message.answer("Ошибка: такого класса нет. Выберите из списка.")
        return

    # Получаем числовой идентификатор class_id
    class_id = animal_class.id

    # Теперь ищем отряды по числовому class_id
    orders = db_session.query(Order).filter(Order.class_id == class_id).all()

    if not orders:
        await message.answer("К сожалению, в этом классе нет отрядов.")
        return

    # Создаем клавиатуру с отрядами
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(order.name))] for order in orders],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer("Выберите отряд:", reply_markup=keyboard)
    await state.set_state(QuizState.choose_order)


@router.message(QuizState.choose_order)
async def process_order_selection(message: Message, state: FSMContext, db_session):
    chat_id = message.from_user.id
    username = message.from_user.username or "unknown"
    is_active = True
    state_str = await state.get_state()
    chosen_animal = "not chosen"
    await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)
    order_name = message.text.strip()
    # Получаем отряд по имени
    animal_order = db_session.query(Order).filter_by(name=order_name).first()
    if not animal_order:
        await message.answer("Ошибка: такого отряда нет. Выберите из списка.")
        return

    # Получаем список семейств, принадлежащих выбранному отряду
    families = db_session.query(Family).filter_by(order_id=animal_order.id).all()
    if not families:
        await message.answer("К сожалению, у этого отряда нет семейств.")
        return

    # Генерируем кнопки для выбора семейства
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(family.name))] for family in families],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Отправляем пользователю сообщение с кнопками выбора
    await message.answer(text="Выберите семейство:", reply_markup=keyboard)
    await state.set_state(QuizState.choose_family)


@router.message(QuizState.choose_family)
async def process_family_selection(message: Message, state: FSMContext, db_session):
    chat_id = message.from_user.id
    username = message.from_user.username or "unknown"
    is_active = True
    state_str = await state.get_state()
    chosen_animal = "not chosen"
    await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)
    family_name = message.text.strip()
    # Получаем семейство по имени
    family = db_session.query(Family).filter_by(name=family_name).first()
    if not family:
        await message.answer("Ошибка: такого семейства нет. Выберите из списка.")
        return

    # Получаем список родов для выбранного семейства
    genera = db_session.query(Genus).filter_by(family_id=family.id).all()
    if not genera:
        await message.answer("К сожалению, у этого семейства нет родов.")
        return

    # Генерируем кнопки для выбора рода
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(genus.name))] for genus in genera],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Отправляем пользователю сообщение с кнопками выбора
    await message.answer(text="Выберите род:", reply_markup=keyboard)
    await state.set_state(QuizState.choose_genus)


@router.message(QuizState.choose_genus)
async def process_genus_selection(message: Message, state: FSMContext, db_session):
    chat_id = message.from_user.id
    username = message.from_user.username or "unknown"
    is_active = True
    state_str = await state.get_state()
    chosen_animal = "not chosen"
    await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)
    genus_name = message.text.strip()
    # Получаем род по имени
    genus = db_session.query(Genus).filter_by(name=genus_name).first()
    if not genus:
        await message.answer("Ошибка: такого рода нет. Выберите из списка.")
        return

    # Получаем список животных в выбранном роде
    animals = db_session.query(Animal).filter_by(genus_id=genus.id).all()
    if not animals:
        await message.answer("К сожалению, у этого рода нет животных.")
        return
    await message.answer(
        text="В Московском зоопарке есть такие животные выбранного Вами рода:",
        reply_markup=ReplyKeyboardRemove(),
    )
    # Создаем inline-кнопки с названиями и фото животных
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for animal in animals:
        # Добавляем кнопку с именем животного и URL для фото
        button = InlineKeyboardButton(
            text=animal.name, callback_data=f"animal_{animal.id}"
        )
        inline_keyboard.inline_keyboard.append([button])

        # Отправляем фото перед кнопкой
        if animal.image_url:  # Убедитесь, что в модели Animal есть поле `photo_url`
            await message.answer_photo(
                photo=animal.image_url,
                caption=animal.name,
                reply_markup=ReplyKeyboardRemove(),
            )

    # Отправляем клавиатуру
    if inline_keyboard.inline_keyboard:
        await message.answer("Выберите животное:", reply_markup=inline_keyboard)
        await state.set_state(QuizState.choose_animal)
        chat_id = message.from_user.id
        username = message.from_user.username or "unknown"
        is_active = True
        state_str = await state.get_state()
        chosen_animal = "not chosen"
        await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)
    else:
        await message.answer("К сожалению, у этого рода нет животных.")


@router.callback_query(F.data.startswith("animal_"))
async def process_animal_callback(callback_query, state: FSMContext, db_session):
    animal_id = int(callback_query.data.split("_")[1])
    # Получаем информацию о животном из базы данных
    animal = db_session.query(Animal).filter_by(id=animal_id).first()
    if not animal:
        await callback_query.message.answer("Ошибка: животное не найдено.")
        return

    # Отправляем сообщение с результатом викторины
    result_message = (
        f"Вы выбрали животное: {animal.name}. Поздравляем!\n"
        f"Напишите сотруднику, чтобы стать опекуном :)\n"
    )

    # Добавляем ссылку в результат
    result_message += "<a href='https://moscowzoo.ru/about/guardianship'>Подробнее о программе опеки</a>"

    await callback_query.message.answer(
        result_message,
        parse_mode="HTML",  # Указываем, что используем HTML-разметку
        reply_markup=ReplyKeyboardRemove(),
    )

    # Отправляем фото
    await callback_query.message.answer_photo(
        photo=animal.image_url, reply_markup=ReplyKeyboardRemove()
    )

    # Обновляем состояние пользователя в базе данных
    chat_id = callback_query.from_user.id
    username = callback_query.from_user.username or "unknown"
    is_active = False
    state_str = "The animal was chosen"
    chosen_animal = str(animal.name)
    await save_user_to_db(chat_id, username, is_active, state_str, chosen_animal)

    await callback_query.message.answer(
        "Для того чтобы: \n"
        "- связаться с сотрудником зоопарка нажмите /contacts \n"
        "- поделиться результатами в соцсетях нажмите /share \n"
        "- попробовать пройти викторину еще раз нажмите /start"
    )
    await state.clear()
