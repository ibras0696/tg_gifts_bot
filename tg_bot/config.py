import os

import dotenv

dotenv.load_dotenv()

# Токен бота
TOKEN_BOT = os.getenv('TOKEN_BOT')

# Разбор ID админов переданный в env и преобразование
def raz_admins(s: str) -> list[int]:
    txt = s.split(',')
    st = [int(i) for i in txt]
    return st

# Айди Администратора TG
ADMIN_IDS = raz_admins(os.getenv('ADMIN_IDS'))

# print(BOT_TOKEN, API_ID, API_HASH)