import logging
import sys
from datetime import datetime
from typing import List

import pytz
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from config import config
from tgbot.models.users import User

logger = logging.getLogger("telegram_bot.BannedMiddleware")


class BannedMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_update(self, obj: types.Update, data, *args):
        """Checks ids from users messages to find coincidences in block list
        and prevent sending updates to blocked users
        """

        try:
            users_repo: List[User]
            users_repo = obj.bot["dp_repository"]["users"]
        except KeyError:
            return logger.warn(
                "Bot has no existing users repository for taking banned users list."
                "BannedMiddleware is not working"
            )
        now = datetime.now(tz=pytz.timezone(config.program.timezone))
        banned_users = filter(
            lambda user: user.unbanned_date and user.unbanned_date > now, users_repo
        )
        banned_users_ids = list(user.id for user in banned_users)

        text = (
            f"Вы заблокированы, обратитесь к "
            "администрации {config.misc.support_mention}"
        )
        if obj["message"]:
            if str(obj.message.from_user.id) in banned_users_ids:
                sys.stdout.flush()
                await obj.message.answer(text)
                raise CancelHandler
        elif obj["callback_query"]:
            if str(obj.callback_query.from_user.id) in banned_users_ids:
                await obj.callback_query.message.answer(text)
                raise CancelHandler
