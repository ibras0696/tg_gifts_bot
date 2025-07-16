from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def inline_keyboard_buttons(buttons_dct: dict, starts: str='', adjust: int=2, url_btn: bool= False) -> InlineKeyboardMarkup:
    '''
    Функция возвращает несколько кнопок
    :param buttons_dct: Словарь {кнопка: ссылка или callback}
    :param starts: Начало callback
    :param adjust: общий ряд сколь кнопок должно быть в ряд
    :param url_btn: Если поставить True передаваться будут ссылки
    :return: InlineKeyboardMarkup
    '''
    try:
        if url_btn:
            kb = InlineKeyboardBuilder()
            for key, value in buttons_dct.items():
                kb.add(InlineKeyboardButton(text=key, url=value))
            return kb.adjust(adjust).as_markup()
        else:
            kb = InlineKeyboardBuilder()
            for key, value in buttons_dct.items():
                if key and value:
                    kb.add(InlineKeyboardButton(text=key, callback_data=f'{starts}{value}'))
            return kb.adjust(adjust).as_markup()
    except Exception as ex:
        raise f'Ошибка: {ex}'


# После кнопки старт
start_kb = inline_keyboard_buttons(
    buttons_dct={
        '🎓 Проверить Статус': 'status',
        '💳 Продлить подписку' : 'pay',
        '🏆 Профиль': 'profile',
        '🛠 О Боте': 'bot',
    },
    adjust=1,
    starts='start_'
)


profile_kb = inline_keyboard_buttons(
    buttons_dct={
#        '💸 Снять деньги' : 'take',     # Кнопка для вывода баланса
        '🔙 Назад'         : 'back'     # Вернуться в главное меню или на шаг назад
    },
    adjust=1,  # По одной кнопке в ряд
    starts='profile_'  # Префикс callback-данных
)


# КБ покупки курса
pay_course_kb = inline_keyboard_buttons(
    buttons_dct={
        '💳 Оплатить курс': 'pay',
        '🛠 Поддержка': 'support',
        '🔙 Назад': 'back',
    },
    adjust=1,
    starts='pay_'
)

support_kb = inline_keyboard_buttons(
    buttons_dct={
        '🔙 Назад': 'back',
    },
    starts='support_'
)