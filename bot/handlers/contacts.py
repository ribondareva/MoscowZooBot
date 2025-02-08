from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from bot.utils.config import config

router = Router()


@router.message(Command("contacts"))  # Здесь мы используем Command вместо 'commands'
async def contact_us(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше имя.")
    await state.set_state("waiting_for_name")


@router.message(StateFilter("waiting_for_name"))
async def get_name(message: Message, state: FSMContext):
    user_name = message.text.strip()
    await state.update_data(user_name=user_name)
    await message.answer("Спасибо, теперь напишите свой вопрос.")
    await state.set_state("waiting_for_question")


@router.message(StateFilter("waiting_for_question"))
async def get_question(message: Message, state: FSMContext, bot: Bot):
    user_question = message.text.strip()
    user_data = await state.get_data()
    user_name = user_data.get("user_name")

    # Формируем сообщение для сотрудника
    contact_message = (
        f"От пользователя {user_name} @{message.from_user.username}:\n\n{user_question}"
    )

    # Отправляем сообщение сотруднику
    # from bot.main import bot

    await bot.send_message(config.support_chat_id, contact_message)

    # Подтверждаем, что сообщение отправлено
    await message.answer(
        "Ваш вопрос был отправлен сотруднику. Мы свяжемся с вами скоро."
    )
    await state.clear()
