from database import CrudeUser, CrudeSubscriptions


# 👋 Стартовое сообщение
start_text = (
    "👋 Приветствую тебя, друг! Добро пожаловать в моего Telegram-бота по продаже авторских курсов 🎓📚"
)

# ℹ️ Информация о боте
info_bot_text = (
    "✨ <b>Возможности бота:</b>\n"
    "При оформлении <b>Premium-подписки</b> ты получаешь доступ в закрытый Telegram-канал.\n\n"
    "🎁 В канале ты будешь первым получать <b>уведомления о новых подарках в Telegram</b> — сразу при их появлении!\n\n"
    "📲 Успевай купить подарки раньше всех!"
)

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
    "\n\n🎉 Ты успешно купил премиум!\n📚 Удачного пользования!\n\n"
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
        profile_lines.append(f"⏳ Доступ: {subscription.day_count}")

    return "\n".join(profile_lines)
