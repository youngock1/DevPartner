from aiogram.types import Message
from aiogram import Router, F

from aiogram.fsm.context import FSMContext

from utils.states import Form_anket

from keyboards.reply import rm_kb


router = Router()  # Инифциализация роутера


@router.message(F.text)  # Обработчик текста
async def handler_text(message: Message, state: FSMContext):
    if message.text == 'Смотреть анкеты 🔍':
        pass
    elif message.text == 'Заполнить анкету заново 🔄':
        await message.answer(
            "<b>Введите имя фамилию:</b>",
            parse_mode='html',
            reply_markup=rm_kb
        )
        await state.set_state(Form_anket.full_name)
    elif message.text == 'Отключить анкету 💤':
        pass
    elif message.text == 'Лайк 👍':
        pass
    elif message.text == 'Дизлайк 👎':
        pass
