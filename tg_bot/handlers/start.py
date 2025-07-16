from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import CrudeUser
from ..utils import message_texts
from ..keyboards.common import start_kb, pay_course_kb

router = Router()


# Обработка обычного старта
@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    # Очистка состояний
    await state.clear()
    # Добавляем в Базу
    await CrudeUser().add_user(telegram_id=message.from_user.id,
                               user_name=message.from_user.username)

    await message.answer(message_texts.start_text, reply_markup=start_kb)


@router.callback_query(F.data.startswith('start_'))
async def update_start_cmd(call_back: CallbackQuery):
    tg_id = call_back.message.chat.id
    match call_back.data.replace('start_', ''):
        case 'status':
            await call_back.message.edit_text(message_texts.start_text, reply_markup=start_kb)
        case 'pay':
            await call_back.message.edit_text(message_texts.pay_time_text, reply_markup=pay_course_kb)
        case 'profile':
            await call_back.message.edit_text(await message_texts.get_profile_text(telegram_id=tg_id), reply_markup=start_kb)
        case 'bot':
            await call_back.message.edit_text(message_texts.info_bot_text, reply_markup=start_kb)
        case _:
            pass

