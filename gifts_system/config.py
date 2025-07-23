import os

import dotenv

dotenv.load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Разбор ID админов переданный в env и преобразование
def raz_admins(s: str) -> list[int]:
    txt = s.split(',')
    st = [int(i) for i in txt]
    return st

# Айди Администратора TG
ADMIN_IDS = raz_admins(os.getenv('ADMIN_IDS'))

# Айди Групп
GRPS = raz_admins(os.getenv('GROUP_IDS'))