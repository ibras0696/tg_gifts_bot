import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import TOKEN_BOT, GRPS

from database import init_db


async def push_bot_group_message(txt: str):
    # Телеграм бот
    bot_tg = Bot(token=TOKEN_BOT)
    # Получение списка администраторов группы
    try:
        await bot_tg.send_message(chat_id=GRPS[0], text=txt)
    finally:
        await bot_tg.close()


