import asyncio
import sys
from typing import List, Union

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class BannedMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_update(self, obj: types.Update, data, *args):
        """Checks ids from users messages to find coincidences in block list
        and prevent sending updates to blocked users
        """
        banned_users = obj.bot.get("banned_users")
        config = obj.bot.get("config")
        text = f"Вы заблокированы, обратитесь к администрации {config.misc.support_mention}"
        if obj["message"]:
            if str(obj.message.from_user.id) in banned_users:
                sys.stdout.flush()
                await obj.message.answer(text)
                raise CancelHandler
        if obj["callback_query"]:
            if str(obj.callback_query.from_user.id) in banned_users:
                await obj.callback_query.message.answer(text)
                raise CancelHandler
