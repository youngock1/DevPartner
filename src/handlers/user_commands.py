from aiogram.filters import CommandStart, Command
from keyboards import reply
from aiogram.types import Message
from aiogram import Router, F


router = Router() # Инициализация роутера


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"Добро пожаловать в бота, {message.from_user.full_name}!", reply_markup=reply.main_kb)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(f"Руководство бота...")