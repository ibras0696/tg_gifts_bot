from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database import CrudeUser, CrudeSubscriptions
from utils import message_texts
from keyboards.common import start_kb, pay_course_kb

router = Router()


# Обработка команды /start
@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()  # Очистка FSM

    # Добавление пользователя в базу
    await CrudeUser().add_user(
        telegram_id=message.from_user.id,
        user_name=message.from_user.username
    )

    await message.answer(
        text=message_texts.start_text,
        reply_markup=start_kb
    )


@router.callback_query(F.data.startswith('start_'))
async def update_start_cmd(callback: CallbackQuery) -> None:
    await callback.answer()  # Удаление мигающей кнопки

    tg_id = callback.message.chat.id
    action = callback.data.removeprefix('start_')

    try:
        match action:
            case 'status':
                await callback.message.edit_text(
                    text=message_texts.status_txt,
                    reply_markup=start_kb,
                    parse_mode='HTML'
                )
            case 'pay':
                has_subscription = await CrudeSubscriptions().check_subscription(telegram_id=tg_id)
                if has_subscription:

                    profile_text = await message_texts.get_profile_text(telegram_id=tg_id)
                    await callback.message.edit_text(
                        text=profile_text,
                        reply_markup=start_kb
                    )
                else:
                    await callback.message.edit_text(
                        text=message_texts.pay_time_text,
                        reply_markup=pay_course_kb
                    )

            case 'profile':
                profile_text = await message_texts.get_profile_text(telegram_id=tg_id)
                await callback.message.edit_text(
                    text=profile_text,
                    reply_markup=start_kb
                )

            case 'bot':
                await callback.message.edit_text(
                    text=message_texts.info_bot_text,
                    reply_markup=start_kb,
                    parse_mode='HTML'
                )

            case _:
                pass  # Игнор неизвестных действий

    except TelegramBadRequest as e:
        if 'message is not modified' not in str(e):
            raise
        # Иначе игнорируем ошибку "message is not modified"
