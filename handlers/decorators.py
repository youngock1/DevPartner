"""----------IMPORT MODULES----------"""
from functools import wraps
from aiogram.types import Message
from database.constants import ADMIN_IDS


def admin_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("⛔ У вас нет прав администратора")
            return
        return await func(message, *args, **kwargs)
    return wrapper
