from database import CrudeUser, CrudeSubscriptions, Subscriptions, CrudePayments


# Кнопка старт
start_text = '👋 Приветствую тебя, друг! Добро пожаловать в моего Telegram-бота по продаже авторских курсов 🎓📚'

info_bot_text = (
    "✨ <b>Возможности бота:</b>\n"
    "При оформлении <b>Premium-подписки</b> ты получаешь доступ в закрытый Telegram-канал.\n\n"
    "🎁 В канале ты будешь первым получать <b>уведомления о новых подарках в Telegram</b> — сразу при их появлении!\n\n"
    "📲 Успевай купить подарки раньше всех!"
)
# Функция для получения текста о профиле
async def get_profile_text(telegram_id: int) -> None | str:
    sub_con = await CrudeSubscriptions().get_user_subscriptions(telegram_id)
    user = await CrudeUser().get_user(telegram_id)
    if user:
        txt_user = (
            # f'🆔 Уникальный ID: {user.id}'
            f'\n👤 Telegram ID: {user.telegram_id}'
            f'\n📛 Имя пользователя: {user.user_name}'
            f'\n{f'⏳ Доступ: {sub_con.day_count}' if sub_con else ''}'
        )
        return txt_user
    else:
        return None


status_txt = (
    "📛 Сейчас нет новых подарков.\n"
    "✅ Как только появятся — ты сразу получишь пуш-уведомление!"
)

# Текст отсутствия подписки
no_subs_text = (
    "❌ У тебя нет активной подписки Premium.\n"
    "💳 Чтобы получить доступ к закрытому каналу, "
    "оформи подписку на курс в меню ниже."
)
# КБ покупки
pay_course_text = '💳 Оплата курса: '

# 🧾 Меню оплаты
pay_time_text = "💳 Меню оплаты"

# ✅ Успешная покупка курса
accept_course_text = "\n\n🎉 Ты успешно купил премиум!\n📚 Удачного пользования!"

# 🛠️ Техническая поддержка
support_message_text = (
    "🛠️ Техническая поддержка\n"
    "👤 @this_is_originall"
)

# ⏳ Уведомление о скором окончании подписки
async def push_subs_text(day: int) -> str:
    return (
        f"⚠️ Ваша подписка Премиум скоро закончится!\n"
        f"📅 Осталось: {day} дней"
    )

# ❌ Уведомление об окончании подписки
async def end_push_sub_text(plan: str) -> str:
    return f"🚫 Ваша подписка {plan} завершилась."
