from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot


# Функция кикает пользователей с группы
async def kick_user_if_not_admin(bot: Bot, user_id: int, group_id: int):
    try:
        member = await bot.get_chat_member(chat_id=group_id, user_id=user_id)

        if member.status in ["administrator", "creator"]:  # creator = владелец группы
            pass

        await bot.ban_chat_member(chat_id=group_id, user_id=user_id)
        await bot.unban_chat_member(chat_id=group_id, user_id=user_id)
        print(f"✅ Пользователь {user_id} удалён из группы {group_id}")

    except TelegramBadRequest as e:
        print(f"⚠️ Ошибка удаления {user_id} из {group_id}: {e}")
