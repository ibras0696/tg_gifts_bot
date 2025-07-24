from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards import start_kb
from utils import message_texts

router = Router()


# Вынесенная функция показа главного меню
async def show_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text=message_texts.start_text,
        reply_markup=start_kb
    )


# Обработка кнопок профиля
@router.callback_query(F.data.startswith('profile_'))
async def handle_profile_query(callback: CallbackQuery) -> None:
    await callback.answer()  # Удаление мигающей кнопки

    match callback.data.removeprefix('profile_'):
        case 'back':
            await show_main_menu(callback)
        case _:
            pass  # Можно добавить логгирование неизвестной команды


# Обработка кнопок поддержки
@router.callback_query(F.data.startswith('support_'))
async def handle_support_query(callback: CallbackQuery) -> None:
    await callback.answer()  # Удаление мигающей кнопки

    match callback.data.removeprefix('support_'):
        case 'back':
            await show_main_menu(callback)
        case 'support':
            pass  # Оставлено, как ты просил (support_support)
        case _:
            pass  # Можно логировать неизвестную кнопку
