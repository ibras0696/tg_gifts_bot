from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS


# Фильтр для команд админа
class AdminTypeFilter(BaseFilter):
    def __init__(self):
        self.ADMIN_IDS = ADMIN_IDS

    async def __call__(self, message: Message):
        return True if message.chat.id in self.ADMIN_IDS else False

# Фильтр для обработок кнопок админа
class AdminCallBackFilter(BaseFilter):
    def __init__(self):
        self.ADMIN_IDS = ADMIN_IDS

    async def __call__(self, call_back: CallbackQuery):
        if not call_back.message:
            return False
        return call_back.message.chat.id in self.ADMIN_IDS

