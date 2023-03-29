import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from sqlalchemy.engine import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm import Session
import pytz

from tgbot.filters.rolefilters import AdminFilter
from tgbot.filters.chatfilters import PrivateFilter
from tgbot.handlers import register_menu, register_misc
from tgbot.middlewares import ObjectsMiddleware, AlbumMiddleware, BannedMiddleware
from tgbot.controllers import MenuController
from tgbot.models import UsersRepository
from tgbot.models.orm.base import Base
from config import config


logger = logging.getLogger("telegram_bot")


def init_repository(session):
    return {
        "users": UsersRepository(session).dict(),
    }


def init_db(bot: Bot):
    logger.debug("Initing database, session and repository")
    login_data = (
        f"{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}"
    )
    url = f"postgresql://{login_data}/{config.db.database}"
    engine = create_engine(url)
    if not database_exists(url):
        create_database(url)

    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    session = Session(engine)
    bot["session"] = session
    bot["db_repository"] = init_repository(session)


def register_all_controllers(bot: Bot):
    logger.debug("Registering controllers.")
    bot["menu_controller"] = MenuController(bot["session"], bot["db_repository"])


def register_all_middlewares(dp):
    logger.debug("Registering middlewares.")
    dp.setup_middleware(ObjectsMiddleware())
    dp.setup_middleware(AlbumMiddleware())
    # dp.setup_middleware(BannedMiddleware())


def register_all_filters(dp):
    logger.debug("Registering filters.")
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(PrivateFilter)


def register_all_handlers(dp):
    logger.debug("Registering handlers.")
    register_menu(dp)
    register_misc(dp)
    # register_admin(dp)


async def take_all_banned_users(users_repo: UsersRepository):
    users = users_repo.list()
    banned_users = []
    for user in users:
        if user.unbanned_date is not None:
            if user["unbanned_date"] > datetime.now(pytz.timezone("Europe/Moscow")):
                banned_users.append(user["user_id"])
    return banned_users


async def setup_tgbot():

    logger.info("Starting bot")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=storage)

    bot["dp"] = dp

    init_db(bot)

    register_all_controllers(bot)
    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # bot["banned_users"] = await take_all_banned_users(bot["user_tables"])

    # Banned users service initialization
    # asyncio.create_task(
    #    banned_users_service(bot["banned_users"], bot["user_tables"], logger)
    # )

    # Ad sending service initialization
    # AdService = AdSendingService(
    #    bot["advertising_tables"], bot["user_tables"], bot, logger
    # )
    # asyncio.create_task(AdService.start(10))

    logger.debug("Telegram bot setup was completed successfully.")

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()

        session = await bot.get_session()
        if session:
            await session.close()

        dp.stop_polling()
        await dp.wait_closed()
