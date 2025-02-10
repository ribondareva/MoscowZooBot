from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.db import get_user_result


router = Router()


@router.message(F.text.casefold() == "/share")
async def share_quiz_result(message: Message, db_session):
    chat_id = message.from_user.id

    # Получаем результаты викторины пользователя из БД
    user_result = await get_user_result(db_session, chat_id)
    chosen_animal = user_result.chosen_animal
    if not user_result or not user_result.chosen_animal:
        await message.answer(
            "Вы ещё не прошли викторину. Пройдите её, чтобы поделиться результатом!"
        )
        return
    share_text = f"Я прошёл викторину и выбрал опекунство над {chosen_animal}! 🐾 Присоединяйся! https://t.me/my_favorite_animal_bot #MoscowZoo"
    share_url = f"https://moscowzoo.ru/about/guardianship"

    # Формируем ссылки для соцсетей
    vk_url = f"https://vk.com/share.php?url={share_url}&title={share_text}"
    tg_url = f"https://t.me/share/url?url={share_url}&text={share_text}"
    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔵 VK", url=vk_url)],
            [InlineKeyboardButton(text="✈️ Telegram", url=tg_url)],
            [InlineKeyboardButton(text="🐦 Twitter", url=twitter_url)],
        ]
    )

    await message.answer(
        "Поделитесь своим результатом в соцсетях:", reply_markup=keyboard
    )
