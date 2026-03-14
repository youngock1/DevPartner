"""----------IMPORT MODULES----------"""
from aiogram.filters import CommandStart, Command
from aiogram import Router
from aiogram.types import Message
from keyboards import reply
from database import db

from database import constants
from keyboards.inline import get_delete_confirmation_keyboard


# Инициализация роутера
router = Router()  



# Обработчик команды /start
@router.message(CommandStart())  
async def start_command(message: Message):
    full_name = message.from_user.full_name
    if db.check_user(message.from_user.id):
        await message.answer(
            f"{constants.GREETING_PART_OF_MESSAGE.format(full_name=full_name)}"
            f"{constants.DEFAULT_MESSAGE}"
            f"<b>Для справки: /help</b>",
            reply_markup=reply.main_kb,
            parse_mode='html'
        )
    else:
        await message.answer(
            f"{constants.GREETING_PART_OF_MESSAGE.format(full_name=full_name)}"
            f"{constants.DEFAULT_MESSAGE}"
            f"<b>Для регистрации анкеты: /registr</b>",
            parse_mode='html'
        )


# Обработчик команды /help
@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(f"<b>Справка бота:</b>\n\n"
                         f"{constants.DEFAULT_MESSAGE}"
                         f"<b>Команды бота:</b>\n\n"
                         f"<b>/start</b> - перезапустить бота.\n"
                         f"<b>/help</b> - команда справки.\n"
                         f"<b>/registr</b> - команда регистрации анкеты.\n"
                         f"<b>/profile</b> - вывод анкеты/профиля.\n"
                         f"<b>/delete</b> - удалить свою анкету.\n\n"
                         f"<b>Обратная связь: 👨‍💻 @Ivan13112, 👨‍💻 @BBP42</b>\n\n"
                         f"<b>👥 TG channel: https://t.me/DevPartner1</b>",
                         parse_mode='html',
                         reply_markup=reply.rm_kb)


# Обработчик команды /profile
@router.message(Command("profile"))  
async def profile_command(message: Message):
    data = db.read_user(message.from_user.id)
    if data:
        await message.answer_photo(
            photo=data[0][3], caption=f'<b>ID:</b>    {int(data[0][0])}\n'
            f'<b>Name:</b>  {data[0][1]}\n'
            f'<b>Age:</b>   {data[0][2]} years\n\n'
            f'<b>Stack:</b> {data[0][4]}\n'
            f'<b>City:</b>  {data[0][5]}\n\n'
            f'<b>About:</b> {data[0][7]}\n\n'
            f'<b>Registartion date:</b>\n{data[0][6]}UTC(+3)',
            parse_mode='html'
        )
    else:
        await message.answer(
            "Для отображения профиля,"
            " необходимо пройти регистрацию в боте.\n/registr"
        )


@router.message(Command("delete"))  # Обработчик команды /delete
async def delete_confirm(message: Message):
    """Запрос подтверждения на удаление анкеты"""

    # Проверяем, есть ли анкета у пользователя
    if not db.check_user(message.from_user.id):
        await message.answer(
            "❌ У вас нет анкеты для удаления!\n\n"
            "Создайте анкету: /registr"
        )
        return

    await message.answer(
        "⚠️ <b>Вы точно хотите удалить свою анкету?</b>\n\n"
        "Это действие нельзя будет отменить!",
        reply_markup=get_delete_confirmation_keyboard(),
        parse_mode='html'
    )
