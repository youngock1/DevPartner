from aiogram.types import Message
from aiogram import Router, F

router = Router() # Инифциализация роутера


@router.message(F.text)
async def handler_text(message: Message):
    if message.text == 'Смотреть анкеты 🔥':
        pass
    elif message.text == 'Заполнить анкету заново 🔄':
        pass
    elif message.text == 'Статистика 📊':
        pass
    elif message.text == 'Лайк 👍':
        pass
    elif message.text == 'Дизлайк 👎':
        pass
    elif message.text == 'Отключить анкету 💤':
        pass
