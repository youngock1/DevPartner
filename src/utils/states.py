from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
from typing import Set


# Класс для управления состоянием регистрации анкет
class Form_anket(StatesGroup):
    full_name = State()  # Состояние получения полного имени пользователя
    age = State()        # Состояние получения возраста пользователя
    photo = State()      # Состояние получения фотографии пользователя
    stack = State()      # Состояние получения стэка разработки пользователя
    city = State()       # Состояние получения города пользователя
    about_self = State()  # Состояние получения описания о себе пользователя


# Класс для управления состоянием пользователя
class UserState(StatesGroup):
    viewing_ankets = State()  # Состояние просмотра анкет


# Класс для хранения данных пользователя
class UserData:
    def __init__(self):
        self.viewed_ankets: Set[int] = set()
        self.liked_ankets: Set[int] = set()
        self.current_index: int = 0
        self.last_activity: datetime = datetime.now()
