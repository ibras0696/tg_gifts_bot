import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import TOKEN_BOT, GRPS

from database import init_db


bot_tg = Bot(token=TOKEN_BOT)

async def push_bot_group_message(txt: str):
    try:
        await bot_tg.send_message(chat_id=GRPS[0], text=txt)
    except TelegramBadRequest as e:
        logging.error(f"Telegram error: {e}")

# В основном файле, при завершении программы
async def on_shutdown():
    await bot_tg.close()


