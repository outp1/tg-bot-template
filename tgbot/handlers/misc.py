from aiogram import Dispatcher, Bot, types 
from aiogram.dispatcher.storage import FSMContext
import sys


# Inline close button handler 
async def inclose(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try: 
        await state.finish()
    except: 
        pass
    await bot.delete_message(chat_id=call.message.chat.id, 
            message_id=call.message.message_id)
        


def register_misc(dp: Dispatcher):
    dp.register_callback_query_handler(inclose, text='inclose', state='*')
    
