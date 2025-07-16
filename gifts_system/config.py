import os

import dotenv

dotenv.load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Api айди с телеграмма
API_ID = os.getenv('API_ID')

# Api хеш с телеграмма
API_HASH = os.getenv('API_HASH')

# Админ Id Телеграмма
ADMIN_ID = os.getenv('ADMIN_ID')


# print(BOT_TOKEN, API_ID, API_HASH)