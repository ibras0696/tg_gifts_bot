import traceback
import logging
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Update, Message, ChatMemberUpdated, CallbackQuery
from aiogram import BaseMiddleware, Bot

from database import CrudeSubscriptions
from config import ADMIN_IDS, GRPS


class ErrorMiddleware(BaseMiddleware):
    """
    Middleware для глобального перехвата ошибок в Aiogram 3.
    При возникновении исключений:
    - логирует ошибку в консоль;
    - отправляет уведомление админу;
    - записывает информацию в базу данных.
    """

    async def __call__(
        self,
        handler: Callable[[Update, dict], Awaitable[Any]],
        event: Update,
        data: dict
    ) -> Any:
        try:
            return await handler(event, data)

        except Exception as e:
            bot: Bot = data.get("bot")
            tb = traceback.format_exc()
            logging.error(f"Ошибка при обработке события: {tb}")

            # Безопасно определяем Telegram ID
            telegram_id = None
            telegram_name = None
            if event.message:
                telegram_id = event.message.from_user.id
                telegram_name = event.message.from_user.username
            elif event.callback_query:
                telegram_id = event.callback_query.from_user.id
                telegram_name = event.callback_query.from_user.username
            elif event.inline_query:
                telegram_id = event.inline_query.from_user.id
                telegram_name = event.inline_query.from_user.username

            # Получаем текущую дату и время
            now = datetime.now()

            # Форматируем в нужный формат
            formatted_time = now.strftime("%H:%M %d.%m.%Y")

            # Отправка админу
            if bot:
                try:
                    for tg_id in ADMIN_IDS:
                        await bot.send_message(
                            chat_id=tg_id,
                            text=f"❌ Ошибка!"
                                 f"\nТелеграм ID: {telegram_id}"
                                 f"\nТелеграм Ник: {telegram_name}"
                                 f"\nВремя: {formatted_time}"
                                 f"\n\n<b>{type(e).__name__}:</b> {e}\n\n<pre>{tb[-700:-1]}</pre>",
                            parse_mode="HTML"
                        )
                except Exception as ex:
                    print(f'Ошибк: {ex}')


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self):
        self.group_tariffs = GRPS  # Используем эту переменную везде

    async def __call__(
        self,
        handler: Callable,
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data['bot']
        chat_id = None
        user_id = None

        # Определяем chat_id и user_id в зависимости от типа события
        if isinstance(event, Message):
            chat_id = str(event.chat.id)
            user_id = event.from_user.id

        elif isinstance(event, ChatMemberUpdated):
            if event.old_chat_member.status == ChatMemberStatus.LEFT and \
               event.new_chat_member.status == ChatMemberStatus.MEMBER:
                chat_id = str(event.chat.id)
                user_id = event.new_chat_member.user.id
            else:
                return await handler(event, data)

        elif isinstance(event, CallbackQuery) and event.message:
            chat_id = str(event.message.chat.id)
            user_id = event.from_user.id

        else:
            return await handler(event, data)

        # Проверяем только если чат в нужных группах
        if chat_id in self.group_tariffs:
            try:
                subscription = await CrudeSubscriptions().check_subscription(user_id)

                if not subscription or subscription.day_count <= 0:
                    try:
                        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                        logging.info(f"❌ {user_id} кикнут из {chat_id}, нет подписки")

                        # Отправляем уведомление админам
                        for admin_id in ADMIN_IDS:
                            await bot.send_message(
                                admin_id,
                                f"👤 Пользователь {user_id} исключён из группы {chat_id}\n"
                                f"📋 Причина: отсутствует активная подписка"
                            )
                    except TelegramBadRequest as e:
                        logging.error(f"⚠️ Ошибка при кике пользователя в {chat_id}: {e}")

            except Exception as e:
                logging.exception(f"❌ Ошибка при проверке подписки: {e}")

        return await handler(event, data)
