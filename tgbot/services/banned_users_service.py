import logging
import asyncio
from logging import Logger
from datetime import datetime

import pytz

from tgbot.misc.abc_classes import UsersList
from tgbot.models import UserTables

async def banned_users_service(banned_users: UsersList, user_tables: UserTables, 
        logger: Logger = logging):
    while True:
        users = await user_tables.take_all_users()
        for user in users:
            if user['unbanned_date'] is not None:
                if (user['unbanned_date'] <= datetime.now(pytz.timezone('Europe/Moscow'))
                        and user['user_id'] in banned_users):
                    while True: 
                        try: 
                            banned_users.remove(user['user_id'])
                        except ValueError:
                            break
                    logger.debug(f'User - {user["user_id"]} - removed from banned list')
        await asyncio.sleep(30)
