import logging
from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext

from tgbot.models import UserTables, ContentTables
from tgbot import keyboards
from tgbot.misc.misclogic import admin_panel
from tgbot.misc.states import AdminStates

#TODO: однострочная панель (кнопки назад, удаление лишних сообщений)

async def admin_panel_start(message: types.Message, logger, bot: Bot, state: FSMContext):
    try: 
        await state.finish()
    except:
        pass
    kbs = keyboards.get_admin_panel_keyboard(bot["config"].tg_bot.admin_panel_buttons)
    kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
    await message.answer("Hello, admin!", reply_markup=kbs)


#Admin panel start buttons
async def admin_panel_actions(call: types.CallbackQuery, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables):
    try:
        await state.finish()
    except:
        pass
    action = call.data.split('_')[1]
    if action == 'stats':    
        content = await admin_panel.take_stats_content(user_tables, logger)
        kbs = keyboards.get_stats_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)
    elif action == 'users':
        content = await admin_panel.take_users_content(user_tables, logger)
        kbs = keyboards.get_users_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)


#All admin panel actions buttons
async def admin_actions(call: types.CallbackQuery, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables):
    data = call.data.split('_')
    action = data[1]
    if action == 'find-user':
        kb = keyboards.inclose(bot["config"].misc.inclose_text)
        msg = await call.message.answer('<b>Введите циферный айди или никнейм юзера через @:</b>', reply_markup=kb)
        await state.update_data(msg=msg)
        await AdminStates.find_user.set()        
    elif action == 'export-stat':
        pass


#find-user action
async def find_user_state(message: types.Message, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables):
    data = await state.get_data()
    try: 
        await bot.delete_message(message.from_user.id, data["message"].message_id)
    except:
        pass
    content = await admin_panel.take_find_user_content(message, user_tables, state, bot, logger)
    if not content:
        return await message.answer('<b>Данные введены неверно. Попробуйте ещё раз:</b>', 
                reply_markup=keyboards.inclose(bot["config"].misc.inclose_text))
    else:
        kb = keyboards.get_user_moderate_keyboard(message.from_user.id)
        kb.add(keyboards.inclose_button(bot["config"].misc.inclose_text))
        await message.answer(content, reply_markup=kb)
        


async def admin_user_actions(call: types.CallbackQuery, bot: Bot, 
        logger: logging.Logger, user_tables: UserTables):
    data = call.data.split()
    action, user = data[1], data[2] 
    if action == 'ban':
        pass        
    elif action == 'edit':
        pass
    elif action == 'send-message': 
        pass


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_panel_start, commands=["adm"], state="*", is_admin=True)
    dp.register_callback_query_handler(admin_panel_actions, lambda call: call.data.startswith('adm-panel_'), state='*')
    dp.register_callback_query_handler(admin_actions, lambda call: call.data.startswith('adm-action_'), state='*')

    dp.register_message_handler(find_user_state, state=AdminStates.find_user)

    dp.register_callback_query_handler(admin_user_actions, lambda call: call.data.startswith('adm-user_'), state='*')
