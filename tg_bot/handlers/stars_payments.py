from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import PreCheckoutQuery, SuccessfulPayment
from aiogram import Bot, Router, F
from aiogram.types import LabeledPrice, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import CrudeUser, CrudeSubscriptions, CrudePayments, Subscriptions
from utils import message_texts

from keyboards import profile_kb

router = Router()


# Обработчик команды оплаты
@router.pre_checkout_query()
async def pre_checkout_handler(query: PreCheckoutQuery):
    # Возможно, проверить наличие товара/состояние
    await query.answer(ok=True)


# Обработчик успешной оплаты
@router.message(F.successful_payment)
async def success_payment_handler(message: Message, state: FSMContext, bot: Bot):
    # Проверяем, что сумма оплаты корректная
    if message.successful_payment.total_amount != 69 or message.successful_payment.total_amount == 1:
        await message.answer("Некорректная сумма оплаты!")
        return

    data = await state.get_data()
    msg_id_del = data.get('message_invoice')
    if msg_id_del:
        try:
            # Удаления инвойся
            await bot.delete_message(chat_id=message.chat.id, message_id=msg_id_del)
        except TelegramBadRequest:
            pass  # логгировать при необходимости

    # Получаем ID пользователя
    user_id = message.from_user.id

    text = await handle_pay(user_id)
    await message.answer(
        text=text,
        reply_markup=profile_kb
    )

    # Очистка состояния после успешной оплаты
    await state.clear()


# Функция для обработки платежа
async def handle_pay(user_id: int):
    days = 30
    price = 69
    # Добавление подписки
    sub = CrudeSubscriptions()
    await sub.add_subscription(user_id, days, price)

    paym = CrudePayments()
    await paym.add_payment(user_id, days, price)

    return message_texts.accept_course_text + await message_texts.get_profile_text(user_id)


# Функция для создания клавиатуры с кнопкой оплаты
def only_pay_keyboard(amount: int = 69):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"Оплатить {amount} ⭐️", pay=True)
    return kb.as_markup()
