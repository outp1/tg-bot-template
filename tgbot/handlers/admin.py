from aiogram import Dispatcher, Bot, types
from tgbot.models import UserTables, ContentTables
from tgbot import keyboards


async def admin_panel_start(message: types.Message, logger, bot):
    logger.info(bot)
    kbs = keyboards.get_admin_panel_keyboard(bot["config"].tg_bot.admin_panel_buttons)
    kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
    await message.answer("Hello, admin!", reply_markup=kbs)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_panel_start, commands=["adm"], state="*", is_admin=True)
