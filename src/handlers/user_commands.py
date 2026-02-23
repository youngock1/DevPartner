from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram import Router, F
from keyboards import reply
from database import db


router = Router()  # Инициализация роутера


@router.message(CommandStart()) # Обработчик команды /start
async def start_command(message: Message):
    if db.check_user(message.from_user.id):
        await message.answer(f"<b>Добро пожаловать в бота, {message.from_user.full_name}!</b>\n\n"
                             f"Этот бот для людей, которые хотят создать свои IT-startups и проекты.С помощью этого бота ты сможешь найти себе товарища для кодинга, с которым сможешь разработать pet-project или startup, который в будущем станет популярным 👨‍💻\n\n"
                             f"<b>Для справки: /help</b>",
                             reply_markup=reply.main_kb,
                             parse_mode='html')
    else:
        await message.answer(f"<b>Добро пожаловать в бота, {message.from_user.full_name}!</b>\n\n"
                             f"Этот бот для людей, которые хотят создать свои IT-startups и проекты.С помощью этого бота ты сможешь найти себе товарища для кодинга, с которым сможешь разработать pet-project или startup, который в будущем станет популярным 👨‍💻\n\n"
                             f"<b>Для регистрации анкеты: /registr</b>",
                             parse_mode='html')


@router.message(Command('help')) # Обработчик команды /help
async def help_command(message: Message):
    await message.answer(f"<b>Справка бота:</b>\n\n"
                         f"Этот бот для людей, которые хотят создать свои IT-startups и проекты. С помощью этого бота ты сможешь найти себе товарища для кодинга, с которым сможешь разработать pet-project или startup, который в будущем станет популярным 👨‍💻\n\n"
                         f"<b>Команды бота:</b>\n\n"
                         f"<b>/start</b> - перезапустить бота.\n"
                         f"<b>/help</b> - команда справки.\n"
                         f"<b>/registr</b> - команда регистрации анкеты.\n"
                         f"<b>/profile</b> - вывод анкеты/профиля.\n"
                         f"<b>/delete</b> - удалить свою анкету.\n\n"
                         f"Обратная связь: @Ivan13112", 
                         parse_mode='html',
                         reply_markup=reply.rm_kb)
    

@router.message(Command("profile")) # Обработчик команды /profile
async def profile_command(message: Message):
    data = db.read_user(message.from_user.id)
    if data:
        await message.answer_photo(photo=data[0][3], caption=f'<b>ID:</b>    {int(data[0][0])}\n'
                                                          f'<b>Name:</b>  {data[0][1]}\n'
                                                          f'<b>Age:</b>   {data[0][2]} years\n\n'
                                                          f'<b>Stack:</b> {data[0][4]}\n'
                                                          f'<b>City:</b>  {data[0][5]}\n\n'
                                                          f'<b>About:</b> {data[0][7]}\n\n'
                                                          f'<b>Registartion date:</b>\n{data[0][6]}UTC(+3)',
                                   parse_mode='html')
    else:
        await message.answer("Для отображения профиля, необходимо пройти регистрацию в боте.\n/registr")


@router.message(Command("delete")) # Обработчик команды /delete
async def delete(message: Message):
    db.delete_user(message.from_user.id)
    await message.answer("Ваша анкета удалена!\n/registr")
