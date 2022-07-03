import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from tgbot.config import load_config
from tgbot.filters.rolefilters import AdminFilter
from tgbot.filters.chatfilters import PrivateFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.handlers.misc import register_misc
from tgbot.middlewares.objects import ObjectsMiddleware
from tgbot.models import UserTables, ContentTables
from tgbot.misc import botlogging


def register_all_middlewares(dp):
    dp.setup_middleware(ObjectsMiddleware())
#    dp.setup_middleware(LoggingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(PrivateFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_misc(dp)


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

    bot['logger'] = logger

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

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
