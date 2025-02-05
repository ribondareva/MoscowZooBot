# Логика викторины
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bot.services.quiz_logic import get_class_by_name, get_orders
from bot.handlers.states import QuizState

router = Router()

@router.message(QuizState.choose_class)
async def process_class_selection(message: Message, state: FSMContext, db_session):
    class_name = message.text.strip()
    animal_class = get_class_by_name(db_session, class_name)

    if not animal_class:
        await message.answer("Ошибка: такого класса нет. Выберите из списка.")
        return

    # Получаем список отрядов в выбранном классе
    orders = get_orders(db_session, animal_class.id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(order.name))] for order in orders],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Выберите отряд:", reply_markup=keyboard)
    await state.set_state(QuizState.choose_order)


