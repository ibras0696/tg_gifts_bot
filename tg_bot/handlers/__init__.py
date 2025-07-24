from aiogram import Router, F

from .start import router as st
from .admin import router as adm
from .pay_pull import router as pay_pull
from .profile import router as pr
from .stars_payments import router as st_pay



router = Router()


router.include_routers(
    st, # Стартовые команды
    adm, # Админка
    pay_pull, # Оплата
    pr, # Профиль
    st_pay, # Платежи со звёздами

)
