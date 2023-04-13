import pytest
from aiogram import Bot

from tgbot.controllers import MenuController, AdminController
from config import config


@pytest.fixture
def menu_controller(session, db_repository):
    yield MenuController(session, db_repository)


@pytest.fixture()
def admin_controller(session, db_repository):
    bot = Bot(config.tg_bot.token)
    yield AdminController(session, db_repository, bot)
