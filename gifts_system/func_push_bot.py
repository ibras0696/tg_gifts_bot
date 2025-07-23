import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramBadRequest

from config import TOKEN_BOT, GRPS

from database import init_db


async def push_bot_group_message(txt: str):
    # Отправка сообщения в группу
    group_id = GRPS[0]
    # Телеграм бот
    bot_tg = Bot(token=TOKEN_BOT)
    # Получение списка администраторов группы
    await bot_tg.send_message(chat_id=group_id, text=txt)


