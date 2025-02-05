from aiogram.fsm.state import StatesGroup, State


class QuizState(StatesGroup):
    choose_class = State()
    choose_order = State()
    choose_family = State()
    choose_genus = State()
