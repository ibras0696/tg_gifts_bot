import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import BOT_TOKEN, GRPS

from database import init_db


async def push_bot_group_message(txt: str):
    # Отправка сообщения в группу
    group_id = GRPS[0]
    # Телеграм бот
    bot_tg = Bot(token=BOT_TOKEN)
    # Получение списка администраторов группы
    await bot_tg.send_message(chat_id=group_id, text=txt)


