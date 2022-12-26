from aiogram import Dispatcher, Bot, types

from tgbot.models import UserTables


# TODO: example of a prepared message from message_contents
async def user_start(message: types.Message, bot, user_tables: UserTables):
    await user_tables.new_user(message.from_user.id, message.from_user.mention)
    await message.reply("Hello, user!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
