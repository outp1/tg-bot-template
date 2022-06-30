from aiogram import Dispatcher
from aiogram.types import Message
from tgbot.models import UserTables, ContentTables


async def admin_start(message: Message, user_tables: UserTables = None, content_tables: ContentTables = None):
    await message.reply("Hello, admin!")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
