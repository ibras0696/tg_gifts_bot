from database import CrudeUser, CrudeSubscriptions, Subscriptions, CrudePayments


# Кнопка старт
start_text = '👋 Приветствую тебя, друг! Добро пожаловать в моего Telegram-бота по продаже авторских курсов 🎓📚'

info_bot_text = f'Возможности бота  ты получаешь уведомление о новых подарках при подписки премиум'


# Функция для получения текста о профиле
async def get_profile_text(telegram_id: int) -> None | str:
    sub_con = await CrudeSubscriptions().get_user_subscriptions(telegram_id)
    user = await CrudeUser().get_user(telegram_id)
    if user:
        txt_user = (
            f'🆔 Уникальный ID: {user.id}'
            f'\n👤 Telegram ID: {user.telegram_id}'
            f'\n📛 Имя пользователя: {user.user_name}'
            f'\n{f'Количество дней подписки:', sub_con.day_count if sub_con else ''}'
        )
        return txt_user
    else:
        return None


status_txt = ('📛 Нет нечего нового'
              '\nПри новых подарках придет пуш уведомления')

# КБ покупки
pay_course_text = '💳 Оплата курса: '

# 🧾 Меню оплаты
pay_time_text = "💳 Меню оплаты"

# ✅ Успешная покупка курса
accept_course_text = "🎉 Ты успешно купил премиум!\n📚 Удачного пользования!"

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
