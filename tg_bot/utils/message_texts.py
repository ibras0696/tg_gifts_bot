from datetime import date, timedelta, datetime

from database import CrudeUser, CrudeSubscriptions

# 👋 Стартовое сообщение
start_text = '''
👋 Добро пожаловать в NFT Time Bot!

🎁 Здесь ты можешь первым узнать о выходе 
уникальных NFT-подарков 🖼️✨

👇 Жми на меню и и будь с нами🎮📲
'''

pay_info_text = '''
🎯 Возможности:
• 🔔 Автоматические уведомления о новых релизах  
• 💎 Подписка — всего за 79 звёзд Telegram ⭐ в месяц
'''

# ℹ️ Информация о боте
info_bot_text = """
<b>🤖 Этот бот уведомляет вас о выходе новых NFT-подарков 🎁 в Telegram 📲</b>

<pre>⸻</pre>

<b>🎯 Возможности:</b>
• 🔔 <b>Автоматические уведомления</b> о новых релизах  
• 💎 <b>Подписка</b> — всего за <u>79 звёзд Telegram ⭐</u> в месяц

<pre>⸻</pre>

<b>🔄 Как работает:</b>
• 🛰️ Бот <b>непрерывно отслеживает</b> появление новых NFT  
• 📬 Сразу после <b>добавления нового подарка</b> вы получаете уведомление  
• 📍 <b>Проверить статус подписки</b> можно вручную в любое время через меню

<pre>⸻</pre>

<b>📢 Будьте в курсе:</b>

Подписывайтесь на наш канал 📡, чтобы не пропустить новинки и обновления:  
👉 <a href="https://t.me/Nft_News_Crypta">@Nft_News_Crypta</a>
"""

# 📛 Текущий статус подписки
status_txt = (
    "📛 Сейчас нет новых подарков.\n"
    "✅ Как только появятся — ты сразу получишь пуш-уведомление!"
)

# ❌ Нет активной подписки
no_subs_text = (
    "❌ У тебя нет активной подписки Premium.\n"
    "💳 Чтобы получить доступ к закрытому каналу, оформи подписку на курс в меню ниже."
)

# 💳 Текст оплаты
pay_course_text = '💳 Оплата курса:'

# 💳 Меню оплаты
pay_time_text = "💳 Меню оплаты"

# ✅ Успешная покупка
accept_course_text = (
    "\n\n✅ Ваш платёж был успешно завершён. Спасибо за покупку!💸\n\n"
)

# 🛠️ Техническая поддержка
support_message_text = (
    "🛠️ Техническая поддержка\n"
    "👤 @this_is_originall"
)


# ⏳ Уведомление о скором завершении подписки
async def push_subs_text(days_left: int) -> str:
    return (
        "⚠️ Ваша подписка Премиум скоро закончится!\n"
        f"📅 Осталось: {days_left} дней"
    )


# ❌ Завершение подписки
async def end_push_sub_text() -> str:
    return "🚫 Ваша подписка Премиум завершилась."


# 👤 Получение текста профиля пользователя
async def get_profile_text(telegram_id: int) -> str | None:
    user = await CrudeUser().get_user(telegram_id)
    if not user:
        return None

    subscription = await CrudeSubscriptions().get_user_subscriptions(telegram_id)

    profile_lines = [
        f"👤 Telegram ID: {user.telegram_id}",
        f"📛 Имя пользователя: {user.user_name}",
    ]

    if subscription:
        profile_lines.append(f"🔔 Подписка действует до:"
                             f"\n🗓️{get_subscription_end_datetime(subscription.day_count)['date']}"
                             f"\n⏰{get_subscription_end_datetime(subscription.day_count)['time']} ")

    return "\n".join(profile_lines)


# Функция для получения даты и времени окончания подписки
def get_subscription_end_datetime(days: int) -> dict[str, str]:
    """
    Получает дату и время окончания подписки на основе количества дней.

    :param days: Количество дней подписки
    :return: Словарь с ключами 'date' и 'time'
    """
    start_datetime = datetime.now()
    end_datetime = start_datetime + timedelta(days=days)

    return {
        'date': end_datetime.strftime('%d.%m.%Y'),
        'time': end_datetime.strftime('%H:%M:%S')
    }
