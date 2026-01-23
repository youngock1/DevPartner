from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(

    keyboard=
    [
        [KeyboardButton(text='Смотреть анкеты'), KeyboardButton(text='Заполнить анкету заново'), KeyboardButton(text='Статистика')]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

ank_kb = ReplyKeyboardMarkup(
    keyboard=
    [
        [KeyboardButton(text='Лайк'), KeyboardButton(text='Написать'), KeyboardButton(text='Дизлайк'), KeyboardButton(text='Отключить анкету')]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери опцию ниже"
)