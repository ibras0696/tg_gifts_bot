from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice

from database import CrudeUser, CrudeSubscriptions, CrudePayments, Subscriptions
from keyboards import support_kb
from utils import message_texts
from keyboards.common import start_kb, profile_kb

from handlers.stars_payments import only_pay_keyboard

from states import DeleteInvoiceState

router = Router()


@router.callback_query(F.data.startswith('pay_'))
async def pay_cmd(call_back: CallbackQuery, bot: Bot, state: FSMContext):
    # Удаление мигающей кнопки
    await call_back.answer()

    user_id = call_back.message.chat.id
    match call_back.data.replace('pay_', ''):
        case 'pay':
            amount: int = 1  # 69 XTR в копейках

            prices = [
                LabeledPrice(
                    label=f"1 месяц PRO — {amount} XTR",  # Подпись, видно в инвойсе
                    amount=amount
                )
            ]

            msg = await bot.send_invoice(
                chat_id=user_id,
                title=f"Покупка PRO-доступа ({amount} XTR)",  # Название инвойса
                description=f"Вы получите доступ к курсу на 30 дней за {amount} Telegram Stars.",
                payload="pro_month_1",
                currency="XTR",
                prices=prices,
                provider_token="",  # Оставляем пустым для Stars
                reply_markup=only_pay_keyboard(amount),  # Кнопка "Оплатить 69 ⭐️"
            )
            # Сохраняем ID сообщения для возможного удаления
            await state.set_state(DeleteInvoiceState.message_invoice)
            await state.update_data(message_invoice=msg.message_id)

        case 'support':
            await call_back.message.edit_text(message_texts.support_message_text, reply_markup=support_kb)
            await state.clear()
        case 'back':
            await call_back.message.edit_text(message_texts.start_text, reply_markup=start_kb)
            await state.clear()
        case _:
            pass
