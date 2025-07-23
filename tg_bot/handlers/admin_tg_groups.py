from aiogram import Router, Bot
from aiogram.types import ChatJoinRequest, Message, ChatMemberUpdated
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from database import CrudeSubscriptions
from config import GRPS

router = Router()

# Обработка заявок на вступление
@router.chat_join_request()
async def handle_join_request(request: ChatJoinRequest, bot: Bot):
    user_id = request.from_user.id
    chat_id = request.chat.id

    if chat_id in GRPS:
        sub_user = await CrudeSubscriptions().check_subscription(telegram_id=user_id)
        if sub_user and sub_user.day_count > 0:
            await bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            return

    # ❌ Отклоняем без блокировки (не баним!)
    await bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)


@router.chat_member()
async def kick_on_join_if_no_sub(event: ChatMemberUpdated):
    # Проверяем, стал ли участником
    if event.old_chat_member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED) and \
       event.new_chat_member.status == ChatMemberStatus.MEMBER:

        user_id = event.from_user.id
        chat_id = event.chat.id

        if chat_id in GRPS:  # Проверяем, что группа в списке разрешённых

            try:
                subscription = await CrudeSubscriptions().check_subscription(user_id)

                if not subscription or subscription.day_count <= 0:
                    try:
                        await event.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                        await event.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
                        print(f"❌ {user_id} кикнут при входе в {chat_id}")
                    except TelegramBadRequest as e:
                        print(f"⚠️ Ошибка при кике: {e}")
            except Exception as e:
                print(f"❌ Ошибка при проверке подписки: {e}")

