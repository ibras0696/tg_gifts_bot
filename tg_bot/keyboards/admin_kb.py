from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from keyboards import inline_keyboard_buttons


# Кнопки для админ панели
cmd_admin_kb = inline_keyboard_buttons(
    buttons_dct={
        '📊 Подписки': 'subs',
        '👥 Пользователи': 'users',
        '📝 Платежи': 'payments',
    },
    adjust=1,
    starts='admin_',
)
