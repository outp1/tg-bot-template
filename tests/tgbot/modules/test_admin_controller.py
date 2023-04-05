from datetime import datetime

from aiogram.types import InlineKeyboardMarkup
import pytest

from tgbot.controllers.admin import AdminController
from tgbot.models.users import User
from config import config


async def test_start(admin_controller: AdminController):
    text, kb = await admin_controller.start()
    assert text == "Hello, admin!"
    assert isinstance(kb, InlineKeyboardMarkup)


async def test_stats_panel(admin_controller: AdminController):
    text, kb = await admin_controller.stats_panel()
    assert "Statistics of the" in text
    assert isinstance(kb, InlineKeyboardMarkup)


async def test_users_panel(admin_controller: AdminController):
    text, kb = await admin_controller.users_panel()
    assert f"The <b>{config.tg_bot.bot_name}</b> users panel" in text
    assert isinstance(kb, InlineKeyboardMarkup)


async def test_adverts_panel(admin_controller: AdminController):
    text, kb = await admin_controller.adverts_panel()
    assert "The advert panel of the" in text
    assert isinstance(kb, InlineKeyboardMarkup)


async def test_get_user_info_panel(admin_controller: AdminController):
    user = User(id=123, username="testuser", created_at=datetime.now(), ban_date=None)
    text, kb = await admin_controller.get_user_info_panel(user)
    assert "User Information" in text
    assert "Registration date" in text


async def test_find_user(admin_controller: AdminController):
    # Register user to find
    admin_controller.users_repo.add(User(id=123456, username="testuser"))

    # Test finding user by ID
    text, kb = await admin_controller.find_user("123456")
    assert "User Information" in text

    # Test finding user by username
    text, kb = await admin_controller.find_user("testuser")
    assert "User Information" in text

    # Test invalid input
    text, kb = await admin_controller.find_user("invalid input")
    assert "Not a Telegram ID or username" in text

    # Test user not found
    text, kb = await admin_controller.find_user("456")
    assert "User was not found" in text
