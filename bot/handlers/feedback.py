# Обратная связь (отправляется админу)
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot.models.feedback import Feedback
from bot.utils.config import config
from bot.utils.db import async_session_maker
from bot.handlers.states import FeedbackState

router = Router()


# Команда /feedback — запрос отзыва
@router.message(F.text.lower() == "/feedback")
async def ask_feedback(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True
    )
    await message.answer("Напишите ваш отзыв:", reply_markup=keyboard)
    await state.set_state(FeedbackState.waiting_for_feedback)


# Обрабатываем введенный отзыв
@router.message(FeedbackState.waiting_for_feedback, F.text)
async def process_feedback(message: Message, state: FSMContext):
    feedback_text = message.text

    if feedback_text.lower() == "отмена":
        await message.answer("Отправка отзыва отменена.", reply_markup=None)
        await state.clear()
        return

    # Сохраняем отзыв в базу
    async with async_session_maker() as session:
        new_feedback = Feedback(
            user_id=message.from_user.id,
            username=message.from_user.username,
            text=feedback_text,
        )
        session.add(new_feedback)
        await session.commit()

    # Отправляем отзыв админам
    await message.bot.send_message(
        config.support_chat_id,
        f"📢 Отзыв от @{message.from_user.username}:\n\n{feedback_text}",
    )

    # Подтверждаем отправку пользователю
    await message.answer("Спасибо за ваш отзыв! 😊", reply_markup=None)
    await state.clear()
