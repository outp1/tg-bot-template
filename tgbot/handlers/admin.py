from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext

from tgbot.models import UserTables, ContentTables
from tgbot import keyboards
from tgbot.misc.misclogic import admin_panel


async def admin_panel_start(message: types.Message, logger, bot: Bot, state: FSMContext):
    try: 
        await state.finish()
    except:
        pass
    kbs = keyboards.get_admin_panel_keyboard(bot["config"].tg_bot.admin_panel_buttons)
    kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
    await message.answer("Hello, admin!", reply_markup=kbs)


async def admin_panel_actions(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.finish()
    except:
        pass
    action = call.data.split('_')[1]
    if action == 'stats':    
        content = await admin_panel.take_stats_content()
        kbs = keyboards.get_stats_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)
    elif action == 'users':
        content = await admin_panel.take_users_content()
        kbs = keyboards.get_users_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_panel_start, commands=["adm"], state="*", is_admin=True)
    dp.register_callback_query_handler(admin_panel_actions, lambda call: call.data.startswith('adm-panel_'), state='*')
