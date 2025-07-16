from datetime import datetime, timezone, timedelta

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, delete, insert, update, func
from sqlalchemy.ext.asyncio import async_sessionmaker

from .db import async_session, init_db
from .models import User, Payments, Subscriptions


# asyncio.run(init_db())

# Класс для работы с User Таблицей
class CrudeUser:
    """
    Работа с таблицей пользователей
    основные параметры таблицы
    id, telegram_id, user_name, registered_at, referral_id, balance
    """
    def __init__(self):
        self.session: async_sessionmaker = async_session

    # Функция для добавления пользователя
    async def add_user(self,
                       telegram_id: int,
                       user_name: str | None,
                       ) -> bool | None:
        """
        Функция для добавления пользователя,
        с внутренней проверкой существования
        :param telegram_id: Телеграмм Айди
        :param user_name: Ник пользователя | может отсутствовать
        :return: True при существовании пользователя и False при добавлении
        """
        async with self.session() as conn:
            try:
                # Проверка существования пользователя
                check_user = await conn.execute(select(User).where(User.telegram_id == telegram_id))
                if check_user.scalar_one_or_none():
                    return True

                user = User(telegram_id=telegram_id, user_name=user_name)

                conn.add(user)
            except IntegrityError:
                await conn.rollback()
                return True
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при добавлении пользователя в таблице User: {ex}')
            else:
                await conn.flush()
                await conn.commit()
                return False

    # Функция для получения одного пользователя
    async def get_user(self, telegram_id: int) -> User | None:
        """
        Функция для получения одного пользователя по Телеграм айди
        :param telegram_id: Телеграм айди
        :return: Объект User или None если его нет
        """
        async with self.session() as conn:
            try:

                user = await conn.execute(select(User).where(User.telegram_id == telegram_id))
                return user.scalar_one_or_none()

            except SQLAlchemyError as sq_ex:
                raise SQLAlchemyError(f'Ошибка при получении пользователя: {sq_ex}')

            except Exception as ex:
                raise Exception(f'Ошибка при получение пользователя в таблице User: {ex}')

    # Функция для получения всех пользователей
    async def get_all_users(self) -> list[User]:
        """
        Функция для получения всех пользователей
        :return: список пользователей
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(User))
                return result.scalars().all()
            except SQLAlchemyError as ex:
                raise SQLAlchemyError(f'Ошибка при получении всех пользователей: {ex}')
            except Exception as ex:
                raise Exception(f'Ошибка при получении всех пользователей: {ex}')


    # Функция для обновления данных о пользователе
    async def update_user(self, telegram_id: int, user_name: str | None = None) -> bool:
        """
        Обновление данных о пользователе
        :param telegram_id: Телеграм айди
        :param user_name: Ник для изменения
        :return: True, если пользователь найден и обновлен, иначе False
        """

        async with self.session() as conn:
            try:
                user_result = await conn.execute(select(User).where(User.telegram_id == telegram_id))
                user = user_result.scalar_one_or_none()
                if not user:
                    return False

                if user_name is not None:
                    user.user_name = user_name

                await conn.commit()
                return True
            except IntegrityError:
                await conn.rollback()
                return False
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при обновлении пользователя: {ex}')

    # Функция для подсчета общего количества пользователей
    async def count_users(self) -> int:
        """
        Функция для подсчета общего количества пользователей
        :return: Количество пользователей
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(func.count()).select_from(User))
                return result.scalar_one()
            except Exception as ex:
                raise Exception(f'Ошибка при подсчете пользователей: {ex}')


    # Функция для удаления пользователя
    async def delete_user(self, telegram_id: int) -> bool:
        """
        Удалить пользователя по telegram_id
        :return: True если удалено, иначе False
        """
        async with self.session() as conn:
            try:
                user_result = await conn.execute(select(User).where(User.telegram_id == telegram_id))
                user = user_result.scalar_one_or_none()
                if not user:
                    return False

                await conn.delete(user)
                await conn.commit()
                return True
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при удалении пользователя: {ex}')

# Класс дла работы с Subscriptions Таблицей
class CrudeSubscriptions:
    """
    Работа с таблицей подписок
    основные параметры таблицы
    id, telegram_id, registered_at, referral_id, plan, day_count, day, month, year
    """
    def __init__(self):
        self.session: async_sessionmaker = async_session

    # Функция для добавления подписки
    async def add_subscription(self,
                               telegram_id: int,
                               day_count: int,
                               price: int,
                               start_date: datetime | None = None,
                               ) -> bool:
        """
        Добавить подписку пользователю или продлить существующую того же плана.
        :param telegram_id: Telegram ID пользователя
        :param day_count: Количество дней подписки
        :param price: Сумма стоимости подписки
        :param start_date: Дата начала подписки (по умолчанию сейчас)
        :return: True если успешно, False при ошибке
        """
        start_date = start_date or datetime.now(timezone.utc)

        async with self.session() as conn:
            try:
                # Выполняем запрос к таблице Subscriptions — выбираем подписку
                result = await conn.execute(
                    select(Subscriptions)
                    .where(Subscriptions.telegram_id == telegram_id)
                )
                existing_sub = result.scalar_one_or_none()
                # Берём текущее время для сравнения с датами подписки.
                now = datetime.now(timezone.utc)
                # Если подписка для пользователя и этого плана уже существует — переходим к продлению или обновлению
                if existing_sub:
                    # Дата Начала подписки из полей year, month, day.
                    current_start = datetime(existing_sub.year, existing_sub.month, existing_sub.day, tzinfo=timezone.utc)
                    # Вычисляем дату окончания подписки — прибавляем к дате начала количество дней подписки.
                    current_end = current_start + timedelta(days=existing_sub.day_count)

                    if current_end > now:
                        # Подписка ещё активна — продлеваем
                        # Если подписка ещё не закончилась (current_end позже текущего времени), значит продлеваем её
                        new_end = current_end + timedelta(days=day_count)
                        # Считаем новую дату окончания, прибавляя новые дни.
                        total_days = (new_end - current_start).days
                        # Пересчитываем общее количество дней подписки с начала и обновляем поле day_count
                        existing_sub.day_count = total_days

                    # Если подписка уже просрочена, начинаем отсчёт заново с новой даты start_date.
                    else:
                        # Подписка просрочена — начинаем заново
                        existing_sub.day = start_date.day
                        existing_sub.month = start_date.month
                        existing_sub.year = start_date.year
                        existing_sub.day_count = day_count

                    await conn.commit()
                    return True

                # Подписка не найдена — создаём новую
                sub = Subscriptions(
                    telegram_id=telegram_id,
                    day_count=day_count,
                    day=start_date.day,
                    month=start_date.month,
                    year=start_date.year,
                )

                conn.add(sub)
                await conn.commit()
                return True

            except IntegrityError:
                await conn.rollback()
                return False
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при добавлении подписки: {ex}')

    # Функция для увелечения подписки
    async def extend_subscription(self, telegram_id: int, days: int) -> bool:
        """
        Функция для увелечения подписки
        :param telegram_id:

        :param days: количество дней
        :return: True при увеличении и False при отсутствии пользователя
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(
                    select(Subscriptions)
                    .where(Subscriptions.telegram_id == telegram_id)
                )
                sub = result.scalar_one_or_none()

                if sub:
                    sub.day_count += days
                    await conn.commit()
                    return True
                return False
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при увеличении одной подписки: {ex}')

    # Функция для уменьшения подписки одного пользователя
    async def reduce_subscription(self, telegram_id: int, days: int) -> bool:
        """
        Функция для уменьшения одной подписки на N количество дней
        :param telegram_id: Телеграм айди
        :param days: Количество дней
        :return: True при успешном уменьшении или False при количестве 0 дней самой подписки
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(
                    select(Subscriptions)
                    .where(Subscriptions.telegram_id == telegram_id)
                )

                sub = result.scalar_one_or_none()
                if sub and sub.day_count > 0:
                    sub.day_count -= days
                    # Если day_count стал <= 0, значит подписка закончилась — возвращаем False
                    if sub.day_count <= 0:
                        sub.day_count = 0  # На всякий случай, не даём уйти в минус
                        await conn.commit()
                        return True

                    await conn.commit()
                    return True
            except Exception as ex:
                await conn.rollback()
                raise Exception(f'Ошибка при уменьшении подписки одного пользователя: {ex}')
            else:
                return False

    # Функция для уменьшения подписки всех пользователей
    async def all_reduce_subscriptions(self, days: int = 1) -> bool | list[Subscriptions]:
        """
        Функция для уменьшения всех подписок на N количество дней
        :param days: Количество Дней
        :return: True при уменьшении или False
        """
        try:
            async with self.session() as conn:
                result = await conn.execute(select(Subscriptions))
                # Получение всех подписок
                subs = result.scalars().all()
                # Проверка о существовании подписок
                if not subs:
                    return False

                updated = False
                # Прохождение по всем и уменьшении подписок
                for sub in subs:
                    if sub.day_count > 0:
                        sub.day_count = max(0, sub.day_count - days)
                        conn.add(sub)
                        updated = True

                if updated:
                    await conn.commit()
                    return subs
        except Exception as ex:
            await conn.rollback()
            raise Exception(f'Ошибка при уменьшении всех подписок: {ex}')

    # Функция для получения всех данных с таблицы подписок
    async def get_all_users_subscriptions(self) -> list[Subscriptions] | bool:
        """
        Функция для получения всех данных с таблицы подписок
        :return: Список объектов Subscriptions
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(Subscriptions))
                subs = result.scalars().all()
                # Если нет подписок
                if not subs:
                    return False
                return subs
            except Exception as ex:
                raise Exception(f'Ошибка при получения всех данных с таблицы подписок: {ex}')

    # Функция для получения данных о подписках определенного пользователя
    async def get_user_subscriptions(self, telegram_id: int) -> Subscriptions | bool:
        """
        Функция для получения данных о подписках определенного пользователя
        :param telegram_id: Телеграм айди
        :return: объект Subscriptions определенного человека если ничего нет то False
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(Subscriptions).where(Subscriptions.telegram_id == telegram_id))
                subs = result.scalar_one_or_none()
                # Если нет подписок
                if not subs:
                    return False
                return subs
            except Exception as ex:
                raise Exception(f'Ошибка при получения всех данных с таблицы подписок: {ex}')

    # Функция для проверки активности подписки
    async def check_subscription(self, telegram_id: int) -> Subscriptions | None:
        """
        Проверка, есть ли у пользователя активная подписка определенного плана
        :param telegram_id: Telegram ID пользователя
        :return: True если подписка активна (day_count > 0), иначе False
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(
                    select(Subscriptions)
                    .where(Subscriptions.telegram_id == telegram_id)
                )
                sub = result.scalar_one_or_none()
                return sub
            except Exception as ex:
                raise Exception(f'Ошибка при проверке подписки: {ex}')

# Класс дла работы с Payments Таблицей
class CrudePayments:
    """
    Работа с таблицей платежей
    основные параметры таблицы
    id, telegram_id, registered_at, day_count, pay_sum, day, month, year
    """
    def __init__(self):
        self.session: async_sessionmaker = async_session

    # Функция для добавления платежа
    async def add_payment(self,
                          telegram_id: int,
                          day_count: int,
                          pay_sum: int,
                          registered_at: datetime | None = None,
                          ) -> bool:
        """
        Добавляет платёж, если такого ещё не было
        :param telegram_id: Телеграм айди
        :param day_count: Кол-во дней подписки
        :param pay_sum: Сумма оплаты
        :param registered_at: Дата регистрации платежа (по умолчанию текущая)
        :return: True — если добавлено, False — если уже существует
        """
        registered_at = registered_at or datetime.now(timezone.utc)
        day = registered_at.day
        month = registered_at.month
        year = registered_at.year

        async with self.session() as conn:
            try:
                # Проверяем, есть ли уже такой платёж
                result = await conn.execute(
                    select(Payments).where(
                        Payments.telegram_id == telegram_id,
                        Payments.day_count == day_count,
                        Payments.pay_sum == pay_sum,
                        Payments.day == day,
                        Payments.month == month,
                        Payments.year == year
                    )
                )
                existing_payment = result.scalar_one_or_none()

                if existing_payment:
                    return False  # Платёж уже есть


                # Создаём новый платёж
                new_payment = Payments(
                    telegram_id=telegram_id,
                    day_count=day_count,
                    pay_sum=pay_sum,
                    registered_at=registered_at,
                    day=day,
                    month=month,
                    year=year
                )

                conn.add(new_payment)
                await conn.commit()
                return True

            except Exception as ex:
                await conn.rollback()
                raise Exception(f"Ошибка при добавлении платежа: {ex}")

    # Функция для получения всех данных с таблицы Payments
    async def get_all_payments(self) -> list[Payments] | bool:
        """
        Функция для получения всех данных с таблицы Payments
        :return: Список объектов Payments или False при отсутствии
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(Payments))
                payments = result.scalars().all()
                if not payments:
                    return False
                return payments
            except Exception as ex:
                raise Exception(f'Ошибка при получении платежей пользователя: {ex}')

    # Функция для получения данных определенного пользователя с таблицы Payments
    async def get_all_payments_and_user(self, telegram_id: int | None = None) -> list[Payments] | bool:
        """
        Функция для получения данных определенного пользователя с таблицы Payments
        :param telegram_id: Телеграм айди
        :param plan: Тариф
        :return: Список объектов Payments или False при отсутствии
        """
        async with self.session() as conn:
            try:
                result = await conn.execute(select(Payments).where(Payments.telegram_id == telegram_id))

                payments = result.scalars().all()

                if not payments:
                    return False

                return payments
            except Exception as ex:
                raise Exception(f'Ошибка при получении платежей одного пользователя: {ex}')

    # Функция для получения данных определенного чека с таблицы Payments
    async def get_payment_by_id(self, id_payment: str) -> Payments:
        async with self.session() as conn:
            try:
                result = await conn.execute(select(Payments).where(Payments.id == id_payment))

                payments = result.scalar_one_or_none()

                return payments
            except Exception as ex:
                raise Exception(f'Ошибка при получении одного платежа одного пользователя: {ex}')

