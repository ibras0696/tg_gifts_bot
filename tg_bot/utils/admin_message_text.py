from datetime import datetime, timezone

from database import CrudeUser, CrudePayments, CrudeSubscriptions


# Запросы к таблице пользователей
users_crd = CrudeUser()
# Запросы к таблице платежей
payments_crd = CrudePayments()
# Запросы к таблице подписок
subscriptions_crd = CrudeSubscriptions()

# Текст приветствия для админ панели
start_test = (
    "👋 Привет, администратор!\n\n"
    "Это панель управления для администраторов бота.\n"
    "Здесь вы можете управлять пользователями, платежами и подписками.\n\n"
    "Выберите нужный раздел из меню ниже."
)


# Текст Подписок
async def subscription_text():
    """
    Возвращает текст статистики подписок для администратора.
    """
    subs = await subscriptions_crd.get_all_users_subscriptions()

    if subs is False:
        return 'Нет подписок'

    if len(subs) == 0:
        return 'Нет подписок'


    now = datetime.now(timezone.utc)

    # Подписки по дате регистрации
    today_subs = [sub for sub in subs if sub.registered_at.date() == now.date()]
    month_subs = [sub for sub in subs if sub.registered_at.year == now.year and sub.registered_at.month == now.month]
    year_subs = [sub for sub in subs if sub.registered_at.year == now.year]

    # Общее количество активных подписок
    all_subs = len([sub for sub in subs if sub.day_count > 0])

    # Общее количество всех подписок
    nums_all_subs = len([sub for sub in subs if sub.day_count > 0])

    return (
        "📊 Статистика подписок:\n\n"
        f"🗓️ Сегодня: {len(today_subs)}\n"
        f"📅 В этом месяце: {len(month_subs)}\n"
        f"📆 В этом году: {len(year_subs)}\n\n"
        f"🔵 Активных подписок: {all_subs}\n\n"
        f"💰 Общее количество подписок: {nums_all_subs}"
    )

# Текст Пользователей
async def users_text() -> str:
    """
    Возвращает текст со статистикой о таблице пользователей.
    """
    users = await users_crd.get_all_users()

    if users is False:
        return 'Нет пользователей'

    if len(users) == 0:
        return 'Нет пользователей'

    now = datetime.now(timezone.utc)

    # Регистрации по дате
    today_users = [u for u in users if u.registered_at.date() == now.date()]
    month_users = [u for u in users if u.registered_at.year == now.year and u.registered_at.month == now.month]
    year_users = [u for u in users if u.registered_at.year == now.year]


    return (
        "👥 Статистика пользователей:\n\n"
        f"🔢 Всего: {len(users)}\n"
        f"🗓️ Сегодня зарегистрировались: {len(today_users)}\n"
        f"📅 В этом месяце: {len(month_users)}\n"
        f"📆 В этом году: {len(year_users)}\n\n"
    )


# Текст Платежей
async def payments_text() -> str:
    """
    Возвращает текст со статистикой о таблице платежей.
    """
    pays = await payments_crd.get_all_payments()

    if pays is False:
        return 'Нет Платежей'

    if len(pays) == 0:
        return 'Нет Платежей'
    now = datetime.now(timezone.utc)

    # Суммы и фильтры по дате
    today = [p for p in pays if p.registered_at.date() == now.date()]
    month = [p for p in pays if p.registered_at.year == now.year and p.registered_at.month == now.month]
    year = [p for p in pays if p.registered_at.year == now.year]


    return (
        "💳 Статистика платежей:\n\n"
        f"🧾 Всего платежей: {len(pays)}\n"
        f"💰 Общая сумма: {sum(p.pay_sum for p in pays)} ₽\n\n"

        "📊 За период:\n"
        f"   📅 Сегодня: {len(today)} платеж(ей) на сумму {sum(p.pay_sum for p in today)} ₽\n"
        f"   🗓️ В этом месяце: {len(month)} платеж(ей) на сумму {sum(p.pay_sum for p in month)} ₽\n"
        f"   📆 В этом году: {len(year)} платеж(ей) на сумму {sum(p.pay_sum for p in year)} ₽\n\n"
    )
