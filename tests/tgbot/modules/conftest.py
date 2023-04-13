import pytest
from aiogram import Bot

from config import config
from tgbot.controllers import AdminController, MenuController


@pytest.fixture
def menu_controller(session, db_repository):
    yield MenuController(session, db_repository)


@pytest.fixture()
def admin_controller(session, db_repository):
    bot = Bot(config.tg_bot.token)
    yield AdminController(session, db_repository, bot)
