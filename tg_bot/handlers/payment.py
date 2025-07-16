from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import CrudeUser, CrudeSubscriptions, CrudePayments
from ..keyboards import support_kb
from ..utils import message_texts
from ..keyboards.common import start_kb, pay_course_kb, profile_kb

router = Router()


@router.callback_query(F.data.startswith('pay_'))
async def pay_cmd(call_back: CallbackQuery):
    user_id = call_back.message.chat.id
    price = 70
    days = 30
    match call_back.data.replace('pay_', ''):
        case 'pay':
            # Добавление подписки
            sub = CrudeSubscriptions()
            result_course_check = await sub.check_subscription(user_id)
            if result_course_check and result_course_check.day_count > 0:
                await call_back.message.edit_text(text=await message_texts.get_profile_text(user_id),
                                                  reply_markup=profile_kb)
            else:

                await sub.add_subscription(
                    telegram_id=user_id,
                    day_count=days,
                    price=price
                )
                # дОбавление платежа в бд
                paym = CrudePayments()
                await paym.add_payment(
                    telegram_id=user_id,
                    day_count=days,
                    pay_sum=price
                )

                await call_back.message.edit_text(
                    text=message_texts.accept_course_text + await message_texts.get_profile_text(user_id),
                    reply_markup=profile_kb)
        case 'support':
            await call_back.message.edit_text(message_texts.support_message_text, reply_markup=support_kb)
        case 'back':
            await call_back.message.edit_text(message_texts.start_text, reply_markup=start_kb)
        case _:
            pass