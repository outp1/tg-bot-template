from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.controllers import MenuController
from tgbot.models.users import User


async def user_start(message: Message, menu_controller: MenuController):
    await menu_controller.register_user(
        User(id=message.from_user.id, username=message.from_user.mention)
    )
    text, keyboard = await menu_controller.get_start_data()
    await message.answer(text, reply_markup=keyboard)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
