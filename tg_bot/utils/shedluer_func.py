from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TOKEN_BOT
from database import CrudeSubscriptions
from utils.message_texts import push_subs_text, end_push_sub_text


# Экземпляр бота
bot_tg = Bot(token=TOKEN_BOT, parse_mode="HTML")  # Укажи parse_mode, если ты используешь HTML-форматирование


# Основная задача: оповещение и уменьшение подписок
async def users_push_subs(bot: Bot = bot_tg):
    db = CrudeSubscriptions()

    # 1. Оповещение о завершении подписки
    try:
        ending_subs = await db.get_all_users_subscriptions()
        for sub in ending_subs:
            if sub.day_count == 1:
                try:
                    await bot.send_message(sub.telegram_id, await end_push_sub_text())
                except Exception as e:
                    print(f"[❌] Ошибка отправки end_push: {e}")
    except Exception as e:
        print(f"[❌] Ошибка при проверке окончания подписок: {e}")

    # 2. Уменьшение дней подписки и оповещение
    try:
        subs = await db.all_reduce_subscriptions()
        for sub in subs:
            if 0 < sub.day_count < 3:
                try:
                    await bot.send_message(sub.telegram_id, await push_subs_text(sub.day_count))
                except Exception as e:
                    print(f"[❌] Ошибка отправки push_subs_text: {e}")
    except Exception as e:
        print(f"[❌] Ошибка при уменьшении подписок: {e}")


# Настройка шедулера
def setup_scheduler(hour: int = 0, minute: int = 0) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        users_push_subs,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="reduce_subs",
        replace_existing=True,
    )

    scheduler.start()
    print(f"📅 Шедулер запущен — ежедневно в {hour:02d}:{minute:02d} по МСК")
    return scheduler
