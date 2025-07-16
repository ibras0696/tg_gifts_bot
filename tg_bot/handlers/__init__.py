from aiogram import Router, F

from .start import router as st
from .admin import router as adm
from .payment import router as pay


router = Router()


router.include_routers(
    st,
    adm,
    pay
)
