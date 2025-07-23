from aiogram import Bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TOKEN_BOT
from database import CrudeSubscriptions, Subscriptions
from utils.message_texts import push_subs_text, end_push_sub_text


# Экземпляр бота для работы
bot_tg = Bot(token=TOKEN_BOT)


async def users_push_subs(bot: Bot = bot_tg):
    sbu_con = CrudeSubscriptions()
    subs_check = await sbu_con.get_all_users_subscriptions()
    if subs_check:
        for sub in subs_check:
            if sub.day_count == 1:
                try:
                    # айди групп
                    grp_id = Subscriptions.get_group_ids().get(sub.plan)
                    await bot.send_message(sub.telegram_id, await end_push_sub_text(plan=grp_id))
                except:
                    pass
    # Получение данных подписок
    subs = await sbu_con.all_reduce_subscriptions()
    if subs:
        for sub in subs:
            if 0 < sub.day_count < 3:
                await bot.send_message(sub.telegram_id, await push_subs_text(sub.day_count, sub.plan))


def setup_scheduler(hour: int = 0, minute: int = 0) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        users_push_subs,  # ← без ()
        trigger=CronTrigger(hour=hour, minute=minute),
        id="reduce_subs",
        replace_existing=True,
    )

    scheduler.start()
    print("📅 Шедулер запущен (каждый день в 00:00 МСК)")
    return scheduler
