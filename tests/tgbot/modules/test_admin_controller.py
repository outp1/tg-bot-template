from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import AsyncMock, patch

import pytz
from aiogram.types import InlineKeyboardMarkup

from config import config
from tgbot.controllers.admin import AdminController
from tgbot.misc.generate_id import generate_base_id
from tgbot.models.users import User, UsersRepository


def register_user(users_repo: UsersRepository, user: Optional[User] = None):
    if not user:
        user = User(id=generate_base_id(), username="test")
    users_repo.add(user)
    users_repo.session.commit()
    return user


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
    user = User(id=123, username="testuser")
    text, kb = await admin_controller.get_user_info_panel(user)
    assert "User Information" in text
    assert "Registration date" in text


async def test_find_user(admin_controller: AdminController):
    # Register user to find
    admin_controller.users_repo.add(User(id=123456, username="testuser"))

    # Test finding user by ID
    text, kb = await admin_controller.find_user_info("123456")
    assert "User Information" in text

    # Test finding user by username
    text, kb = await admin_controller.find_user_info("testuser")
    assert "User Information" in text

    # Test invalid input
    text, kb = await admin_controller.find_user_info("invalid input")
    assert "User was not found" in text

    # Test user not found
    text, kb = await admin_controller.find_user_info("456")
    assert "User was not found" in text


@patch("aiogram.Bot.send_message")
async def test_ban_user_with_string_time(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

    # Test ban user with string time
    unbanned_date = datetime.now(tz=pytz.timezone(config.program.timezone)) + timedelta(
        hours=1
    )
    await admin_controller.ban_user(test_user, "1h", "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date

    # Test ban user with timedelta
    unbanned_date = unbanned_date + timedelta(hours=1)
    await admin_controller.ban_user(test_user, timedelta(hours=1), "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date

    # Test ban user with no unit and time is being extended
    unbanned_date += timedelta(minutes=15)
    await admin_controller.ban_user(test_user, "15", "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date

    # Test ban user have send message to banned user
    await admin_controller.ban_user(test_user, "1h", "Test ban")
    assert mock_send.await_args
    assert test_user.id == mock_send.await_args[0][0]


@patch("aiogram.Bot.send_message")
async def test_ban_user_action(mock_send: AsyncMock, admin_controller: AdminController):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)

    # Test user can be banned by str ban_time
    text, kb = await admin_controller.ban_user_action(str(user.id), "1h", "Violation")
    assert f"User @{user.username} has been banned until " in text
    assert mock_send.await_args
    assert (
        user.id == mock_send.await_args[0][0]
        and "You were banned" in mock_send.await_args[0][1]
    )
    assert isinstance(kb, InlineKeyboardMarkup)
