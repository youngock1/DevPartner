from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           ReplyKeyboardRemove)

# Основная клавиатура
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Смотреть анкеты 🔍')],
    [KeyboardButton(text='Статистика 📊')],
    [KeyboardButton(text='Мои лайки 👍'), KeyboardButton(
        text='Кто лайкнул меня 🩷')],
    [KeyboardButton(text='Заполнить анкету заново 🔄')]
], resize_keyboard=True, input_field_placeholder='Выберите действие...')

# Клавиатура для просмотра анкет
ank_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Лайк 👍'), KeyboardButton(text='Дизлайк 👎')],
    [KeyboardButton(text='Прекратить просмотр 💤')]
], resize_keyboard=True)

# Клавиатура удаления
rm_kb = ReplyKeyboardRemove()
