from aiogram.fsm.state import StatesGroup, State


class Form_anket(StatesGroup):
    full_name = State()
    age = State()
    photo = State()
    stack = State()
    city = State()
    about_self = State()
