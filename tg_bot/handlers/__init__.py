from aiogram import Router, F

from .start import router as st
from .admin import router as adm
from .pay_pull import router as pay_pull
from .profile import router as pr
from .admin_tg_groups import router as adm_tg_gr


router = Router()


router.include_routers(
    st, # Стартовые команды
    adm, # Админка
    pay_pull, # Оплата
    pr, # Профиль
    adm_tg_gr # Админка для управления группами бота
)
