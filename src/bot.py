from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramNetworkError
from handlers import bot_messages, user_commands, questionare
from aiogram import Bot, Dispatcher
from callbacks import callbacks
from dotenv import load_dotenv
import datetime, asyncio
import logging, sys, os


load_dotenv() # Загружаем переменные окружения


logging.basicConfig( # Настраиваем логгер
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


async def main():

    bot = Bot(token=os.getenv("BOT_TOKEN")) # Инициализация бота
    dp = Dispatcher() # Инициализация диспетчера

    dp.include_routers( # Подключение Роутеров(обработчиков)
        callbacks.router,
        user_commands.router,
        questionare.router,
        bot_messages.router)

    logging.info(f"DevPartner | IT - is launched") # Логирование запуска бота
    await bot.delete_webhook(drop_pending_updates=True) # Удаление обновлений за АФК бота
    await dp.start_polling(bot) # Запуск polling бота


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout) # Логирование всех обновлений в боте(абсолютно всех)
        asyncio.run(main()) # Запуск бота
    except TelegramNetworkError as error_network:
        logging.info(f'Ошибка в подключении: {error_network}.')
    except TelegramAPIError as error_api_connect:
        logging.info(f'Ошибка в подключении API: {error_api_connect}.')
    except TelegramBadRequest as error_bad_request:
        logging.info(f'Некорректный запрос на сервер TG: {error_bad_request}.')
    except KeyboardInterrupt:
        logging.info(f'Прекращена работа программы сочетанием клавиш Cntrl + C.')
