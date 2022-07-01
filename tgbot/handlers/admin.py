from aiogram import Dispatcher, types
from tgbot.models import UserTables, ContentTables
from tgbot.keyboards import inclose


async def admin_start(message: types.Message, logger):
    await message.reply("Hello, admin!", reply_markup=inclose('Отмена'))


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
