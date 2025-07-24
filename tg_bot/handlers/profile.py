from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import start_kb
from utils import message_texts

router = Router()

@router.callback_query(F.data.startswith('profile_'))
async def profile_query(call_back: CallbackQuery):
    # Удаление мигающей кнопки
    await call_back.answer()

    match call_back.data.replace('profile_', ''):
        case 'back':
            await call_back.message.edit_text(text=message_texts.start_text, reply_markup=start_kb)
        case _:
            pass

# Обработка кнопок поддержки назад
@router.callback_query(F.data.startswith('support_'))
async def profile_query(call_back: CallbackQuery):
    # Удаление мигающей кнопки
    await call_back.answer()

    match call_back.data.replace('support_', ''):
        case 'back':
            await call_back.message.edit_text(text=message_texts.start_text, reply_markup=start_kb)
        case _:
            pass