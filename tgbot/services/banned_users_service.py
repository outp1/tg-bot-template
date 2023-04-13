import logging
import asyncio
from datetime import datetime
from typing import List

import pytz
from sqlalchemy.orm import Session

from tgbot.models.users import User, UsersRepository
from config import config


logger = logging.getLogger("telegram_bot.BannedUsersService")


# TODO full refactor
async def banned_users_service(banned_users: List[User], db_session: Session):
    users_repo = UsersRepository(db_session)
    while True:
        users = users_repo.list()
        for user in users:
            if user.unbanned_date is not None:
                if (
                    user.unbanned_date
                    <= datetime.now(pytz.timezone(config.program.timezone))
                    and user.id in banned_users
                ):
                    while True:
                        try:
                            banned_users.remove(user["user_id"])
                        except ValueError:
                            break
                    logger.debug(f'User - {user["user_id"]} - removed from banned list')
        await asyncio.sleep(10)
