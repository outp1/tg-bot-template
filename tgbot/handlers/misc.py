from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import MessageToDeleteNotFound


# Inline close button handler
async def inclose_handler(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.finish()
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )
    await call.answer()


async def multi_inclose_with_state(
    call: types.CallbackQuery, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    await state.finish()
    try:
        for msg in data["msgs"]:
            try:
                await bot.delete_message(
                    chat_id=call.message.chat.id, message_id=msg.message_id
                )
            except AttributeError:
                try:
                    for photo in msg:
                        await bot.delete_message(
                            chat_id=call.message.chat.id, message_id=photo.message_id
                        )
                except MessageToDeleteNotFound:
                    return await call.answer("Ошибка")
    except KeyError:
        pass


def register_misc(dp: Dispatcher):
    dp.register_callback_query_handler(inclose_handler, text="inclose", state="*")

    dp.register_callback_query_handler(
        multi_inclose_with_state, text="multiInclose_with_state", state="*"
    )
