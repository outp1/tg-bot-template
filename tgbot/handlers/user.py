from aiogram import Dispatcher
from aiogram.types import Message


async def user_start(message: Message, bot, logger):
    await message.reply("Hello, user!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
