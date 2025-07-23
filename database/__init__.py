import asyncio

from .models import *
from .crud import *
from .db import *


# __all__ = [
#     'init_db', 'Base', 'DATABASE_URL', # основные компоненты БД
#     'CrudeUser', 'CrudeSubscriptions', 'CrudePayments', # Круд Классы
#     'Payments', 'User', 'Subscriptions'# Таблицы
# ]

asyncio.run(init_db())