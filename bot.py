import asyncio
import logging
from datetime import datetime
import sys

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
import pytz

from tgbot.config import load_config
from tgbot.filters.rolefilters import AdminFilter
from tgbot.filters.chatfilters import PrivateFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.handlers.misc import register_misc
from tgbot.middlewares import (ObjectsMiddleware, AlbumMiddleware, 
        BannedMiddleware)
from tgbot.models import (UserTables, ContentTables, 
        ModeratingHistoryTables, AdvertisingTables)
from tgbot.misc import botlogging, abc_classes
from tgbot.services.banned_users_service import banned_users_service


def register_all_middlewares(dp):
    dp.setup_middleware(ObjectsMiddleware())
    dp.setup_middleware(AlbumMiddleware())
    dp.setup_middleware(BannedMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(PrivateFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_misc(dp)

async def take_all_banned_users(user_tables: UserTables):

    users = await user_tables.take_all_users()
    banned_users = []
    for user in users:
        if user['unbanned_date'] is not None:
            if user['unbanned_date'] > datetime.now(pytz.timezone('Europe/Moscow')):
                banned_users.append(user['user_id'])
    return banned_users

async def main():

    config = load_config(".env")

    logger = botlogging.BotLogging('Main', config.program.logs_folder, config.program.logs_token, 
            config.program.logs_telegram_id, tg_handler_dir='tgbot/misc/botlogging/telegram_errors_handler')
    logger = logger.get_logger()

    logger.info("Starting bot")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    # Db connection objects
    bot['user_tables'] = UserTables(config.db.database, config.db.auth, config.db.tables)
    bot['content_tables'] = ContentTables(config.db.database, config.db.auth, 
            config.db.tables, config.tg_bot.message_contents)
    bot['modhistory_tables'] = ModeratingHistoryTables(config.db.database, config.db.auth, config.db.tables, logger)
    bot['advertising_tables'] = AdvertisingTables(config.db.database, config.db.auth, config.db.tables, logger)

    bot['logger'] = logger

    bot['banned_users'] = await take_all_banned_users(bot['user_tables'])

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # Banned users service initialization
    asyncio.create_task(banned_users_service(bot['banned_users'], bot['user_tables'], logger))


    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
