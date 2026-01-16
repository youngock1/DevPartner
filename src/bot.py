from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio, logging, os


load_dotenv()


bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

async def main():
    ...


if __name__ == '__main__':
    asyncio.run(main())