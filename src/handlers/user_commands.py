from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router

router = Router()  # Инициализация роутера

# Создаем клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Смотреть анкеты 🔥")],
        [KeyboardButton(text="Заполнить анкету заново 🔄")],
        [KeyboardButton(text="Статистика 📊")],
        [KeyboardButton(text="Отключить анкету 💤")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        f"Добро пожаловать в бота, {message.from_user.full_name}!",
        reply_markup=main_keyboard
    )

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("Помощь по использованию бота...")

@router.message(Command("profile"))
async def profile_command(message: Message):
    await message.answer("Ваш профиль...")
