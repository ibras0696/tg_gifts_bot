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


# Цена подписки
amount = 39


@router.callback_query(F.data.startswith('pay_'))
async def pay_cmd(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    await callback.answer()  # Удаление мигающей кнопки

    user_id = callback.message.chat.id
    action = callback.data.removeprefix('pay_')

    match action:
        case 'pay':
            prices = [
                LabeledPrice(
                    label=f"1 месяц PRO — {amount} XTR",
                    amount=amount
                )
            ]

            invoice = await bot.send_invoice(
                chat_id=user_id,
                title=f"Покупка PRO-доступа ({amount} XTR)",
                description=message_texts.pay_info_text,
                payload="pro_month_1",
                currency="XTR",
                prices=prices,
                provider_token="",  # Для Telegram Stars — оставляем пустым
                reply_markup=only_pay_keyboard(amount),
            )

            # Сохраняем ID сообщения с инвойсом для возможного удаления
            await state.set_state(DeleteInvoiceState.message_invoice)
            await state.update_data(message_invoice=invoice.message_id)

        case 'support':
            await callback.message.edit_text(
                text=message_texts.support_message_text,
                reply_markup=support_kb
            )
            await state.clear()

        case 'back':
            await callback.message.edit_text(
                text=message_texts.start_text,
                reply_markup=start_kb
            )
            await state.clear()

        case _:
            pass  # Неизвестное действие — игнорируем
