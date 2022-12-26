from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext
import traceback


# TODO: format exc
async def any_error_handler(update, exception, logger):
    logger.error(exception)


# Inline close button handler
async def inclose_handler(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        await state.finish()
    except:
        pass
    await bot.delete_message(
        chat_id=call.message.chat.id, message_id=call.message.message_id
    )


async def multi_inclose_with_state(
    call: types.CallbackQuery, state: FSMContext, bot: Bot
):
    data = await state.get_data()
    try:
        await state.finish()
    except:
        pass
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
                except:
                    return await call.answer("Ошибка")
    except KeyError:
        pass


def register_misc(dp: Dispatcher):
    dp.register_errors_handler(any_error_handler)
    dp.register_callback_query_handler(inclose_handler, text="inclose", state="*")

    dp.register_callback_query_handler(
        multi_inclose_with_state, text="multiInclose_with_state", state="*"
    )
