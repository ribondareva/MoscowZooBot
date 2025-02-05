from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from bot.handlers.states import QuizState
from bot.services.quiz_logic import get_classes


# Начало викторины
async def start_quiz(message: types.Message, state: FSMContext, db_session):
    classes = get_classes(db_session)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(cls.name))] for cls in classes],  # Генерируем кнопки
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Приветствую Вас! Выберите класс животных:",
        reply_markup=keyboard
    )
    await state.set_state(QuizState.choose_class)