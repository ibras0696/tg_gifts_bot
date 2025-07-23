import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import TOKEN_BOT, GRPS

from database import init_db, CrudeSubscriptions

bot_tg = Bot(token=TOKEN_BOT)
bot_id = 7935583481

crud_sub = CrudeSubscriptions()

async def push_bot_group_message(txt: str):
    try:

        subs = await crud_sub.get_all_users_subscriptions()
        for sub in subs:
            if sub.day_count > 0:
                try:
                    # Отправляем сообщение в группу
                    await bot_tg.send_message(chat_id=sub.telegram_id, text=txt)
                except TelegramBadRequest as e:
                    logging.error(f"Ошибка при отправке сообщения пользователю {sub.telegram_id}: {e}")
        # await bot_tg.send_message(chat_id=bot_id, text=txt)
    except TelegramBadRequest as e:
        logging.error(f"Telegram error: {e}")

# В основном файле, при завершении программы
async def on_shutdown():
    await bot_tg.close()


