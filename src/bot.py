from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
import logging
import os
from callbacks import callbacks
from handlers import bot_messages, user_commands

load_dotenv()


bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def main():
    dp.include_routers(
        callbacks.router,
        user_commands.router,
        bot_messages.router
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
