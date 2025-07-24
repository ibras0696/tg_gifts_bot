import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import TOKEN_BOT
from middlewares import ErrorMiddleware
from database import init_db
from handlers import router
from utils import setup_scheduler

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Экземпляры
bot = Bot(token=TOKEN_BOT, parse_mode="HTML")  # parse_mode пригодится для всех сообщений
dp = Dispatcher()


async def main():
    logging.info("🚀 Инициализация бота...")

    # База данных
    await init_db()
    logging.info("📦 База данных инициализирована")

    # Планировщик задач
    setup_scheduler()

    # Мидлвари
    dp.update.middleware(ErrorMiddleware())

    # Роутеры
    dp.include_router(router)

    # Сброс вебхука, если был
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("🤖 Бот запущен. Ожидаем обновления...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except TelegramBadRequest as e:
        logging.error(f"Telegram API error: {e}")
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.critical("💥 Критическая ошибка:", exc_info=e)
