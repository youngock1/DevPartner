from aiogram.types import Message
from aiogram import Router, F

from aiogram.fsm.context import FSMContext

from utils.states import Form_anket

from keyboards.reply import rm_kb
from keyboards.inline import get_update_anket_keyboard

from database import db


router = Router()  # Инифциализация роутера


@router.message(F.text)  # Обработчик текста
async def handler_text(message: Message, state: FSMContext):
    if message.text == 'Смотреть анкеты 🔍':
        pass
    elif message.text == 'Заполнить анкету заново 🔄':
        if not db.check_user(message.from_user.id):
            await message.answer(
            "❌ У вас нет анкеты для обновления!\n\n"
            "Создайте анкету: /registr")
            return

        await message.answer(
            "⚠️ <b>Вы точно хотите обновить свою анкету?</b>\n\n"
            "Это действие нельзя будет отменить!",
            reply_markup=get_update_anket_keyboard(),
            parse_mode='html')
        
    elif message.text == 'Отключить анкету 💤':
        pass
    elif message.text == 'Лайк 👍':
        pass
    elif message.text == 'Дизлайк 👎':
        pass
