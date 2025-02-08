from aiogram import types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from bot.handlers.states import QuizState
from bot.services.quiz_logic import get_classes


# Создаем роутер для обработки сообщений
router = Router()


# Обработчик команды /start
@router.message(F.text.casefold() == "/start")
async def start_quiz(message: types.Message, state: FSMContext, db_session):
    classes = get_classes(db_session)
    if not classes:
        await message.answer("К сожалению, пока нет данных о классах животных.")
        return

    # Генерация клавиатуры с классами животных
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(cls.name))] for cls in classes],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "Приветствую Вас! Данный бот реализует викторину для поиска опекунов животным Московского зоопарка. \n"
        "Для того чтобы: \n"
        "- завершить викторину нажмите /cancel \n"
        "- оставить отзыв нажмите /feedback \n"
        "- связаться с сотрудником зоопарка нажмите /contacts"
    )
    await message.answer(
        "Животных какого класса вы хотели бы выбрать?", reply_markup=keyboard
    )
    await state.set_state(QuizState.choose_class)
