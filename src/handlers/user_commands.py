from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import reply
from aiogram.types import Message
from aiogram import Router, F
from database import test
import datetime

router = Router()  # Инициализация роутера


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"Добро пожаловать в бота, {message.from_user.full_name}!"
                         f"Этот бот для людей, которые хотят создать свои IT-startups и проекты.С помощью этого бота ты сможешь найти себе товарища для кодинга, с которым сможешь разработать pet-project или startup, который в будущем станет популярным 👨‍💻\n\n"
                         f"Для справки: /help",
                         reply_markup=reply.main_kb)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(f"<b>Справка бота:</b>\n\n"
                         f"<b>/start</b> - перезапустить бота.\n"
                         f"<b>/help</b> - команда справки.\n"
                         f"<b>/registr</b> - команда регистрации анкеты.\n\n"
                         f"Этот бот для людей, которые хотят создать свои IT-startups и проекты.С помощью этого бота ты сможешь найти себе товарища для кодинга, с которым сможешь разработать pet-project или startup, который в будущем станет популярным 👨‍💻\n\n"
                         f"Обратная связь: @Ivan13112", 
                         parse_mode='html')
    

@router.message(Command("profile"))
async def profile_command(message: Message):
    data = test.read_user(message.from_user.id)
    if data:
        await message.answer_photo(photo=data[0][3], caption=f'ID:    {data[0][0]}\n'
                                                          f'Name:  {data[0][1]}\n'
                                                          f'Age:   {data[0][2]}\n'
                                                          f'Stack: {data[0][4]}\n'
                                                          f'City:  {data[0][5]}\n'
                                                          f'About: {data[0][7]}\n'
                                                          f'Registartion date:\n{data[0][6]}'
                                   )
    else:
        await message.answer("Для отображения профиля, необходимо пройти регистрацию в боте.\n/registr")
