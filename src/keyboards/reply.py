from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove



main_kb = ReplyKeyboardMarkup(

    keyboard=
    [
        [KeyboardButton(text='Смотреть анкеты 🔍')],
        [KeyboardButton(text='Заполнить анкету заново 🔄')],
        [KeyboardButton(text='Отключить анкету 💤')]
    ],
    one_time_keyboard=False,
    resize_keyboard=True,
    input_field_placeholder="Выбери опцию ниже"
)


ank_kb = ReplyKeyboardMarkup(
    keyboard=
    [
        [
            KeyboardButton(text='Лайк 👍'),
            KeyboardButton(text='Дизлайк 👎')
        ],
        [
            KeyboardButton(text='In process...')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Выбери опцию ниже"
)


rm_kb = ReplyKeyboardRemove()