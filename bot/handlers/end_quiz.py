# действие отмены викторины
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message(StateFilter(None), Command(commands=["cancel"]))
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    await state.set_data({})
    await message.answer(text="Нечего отменять!", reply_markup=ReplyKeyboardRemove())


@router.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено. Вы можете начать викторину заново! \n Чтобы заново начать нажмите /quiz",
        reply_markup=ReplyKeyboardRemove(),
    )
