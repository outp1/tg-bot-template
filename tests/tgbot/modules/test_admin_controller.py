from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import AsyncMock, patch

import pytz
from aiogram.types import InlineKeyboardMarkup
from pytest import raises

from config import config
from tgbot.controllers.admin import AdminController
from tgbot.misc.exceptions import EntityToEditNotFoundError
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
    text, kb = await admin_controller.find_user_action("123456")
    assert "User Information" in text

    # Test finding user by username
    text, kb = await admin_controller.find_user_action("testuser")
    assert "User Information" in text

    # Test invalid input
    text, kb = await admin_controller.find_user_action("invalid input")
    assert "User was not found" in text

    # Test user not found
    text, kb = await admin_controller.find_user_action("456")
    assert "User was not found" in text


@patch("aiogram.Bot.send_message")
async def test_ban_user_with_string_time(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

    unbanned_date = datetime.now(tz=pytz.timezone(config.program.timezone)) + timedelta(
        hours=1
    )
    await admin_controller.ban_user(test_user, "1h", "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date


@patch("aiogram.Bot.send_message")
async def test_ban_user_with_timedelta(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

    unbanned_date = datetime.now(tz=pytz.timezone(config.program.timezone)) + timedelta(
        hours=1
    )
    await admin_controller.ban_user(test_user, timedelta(hours=1), "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date


@patch("aiogram.Bot.send_message")
async def test_ban_user_with_no_unit(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

    unbanned_date = datetime.now(tz=pytz.timezone(config.program.timezone)) + timedelta(
        minutes=15
    )
    await admin_controller.ban_user(test_user, "15", "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date


@patch("aiogram.Bot.send_message")
async def test_ban_user_extending_time(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

    unbanned_date = datetime.now(tz=pytz.timezone(config.program.timezone)) + timedelta(
        minutes=30
    )
    await admin_controller.ban_user(test_user, "15", "Test ban")
    await admin_controller.ban_user(test_user, "15", "Test ban")
    assert isinstance(test_user.unbanned_date, datetime)
    assert test_user.unbanned_date >= unbanned_date


@patch("aiogram.Bot.send_message")
async def test_ban_user_sends_notice_to_user(mock_send: AsyncMock, admin_controller):
    test_user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, test_user)

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


async def test_simple_user_edit(admin_controller: AdminController):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)

    user.username = "another"
    await admin_controller.edit_user(user)
    edited_user = await admin_controller.find_user(user.id)
    assert edited_user and edited_user.username == user.username


async def test_edit_user_throws_error_with_noexisting_entity(
    admin_controller: AdminController,
):
    user = User(id=123456, username="test")
    user.username = "another"
    with raises(EntityToEditNotFoundError):
        await admin_controller.edit_user(user)


async def test_edit_user_throws_error_with_primary_key_editing(
    admin_controller: AdminController,
):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)

    user.id = 654321
    with raises(EntityToEditNotFoundError):
        await admin_controller.edit_user(user)


async def test_simple_user_edit_action(admin_controller: AdminController):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)
    attr_to_edit, new_value = "username", "another"

    text, kb = await admin_controller.edit_user_action(user.id, "username", new_value)
    edited_user = await admin_controller.find_user(user.id)
    assert edited_user and edited_user.username == new_value
    assert (
        f"Successfully edited <code>{attr_to_edit}</code> to "
        f"<code>{new_value}</code> for a user with id <code>{user.id}</code>" in text
    )


async def test_user_edit_action_with_username(admin_controller: AdminController):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)
    attr_to_edit, new_value = "username", "another"

    text, kb = await admin_controller.edit_user_action(
        user.username, "username", new_value
    )
    edited_user = await admin_controller.find_user(user.id)
    assert edited_user and edited_user.username == new_value
    assert (
        f"Successfully edited <code>{attr_to_edit}</code> to "
        f"<code>{new_value}</code> for a user with id <code>{user.id}</code>" in text
    )


async def test_user_edit_action_with_noexisting_id(admin_controller: AdminController):
    user = User(id=123456, username="test")

    text, kb = await admin_controller.edit_user_action(user.id, "username", "another")
    assert "User to edit was not found" in text


async def test_user_primary_key_edit_action_throws_error(
    admin_controller: AdminController,
):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)

    text, kb = await admin_controller.edit_user_action(user.id, "id", "123")
    assert "Primary key can't be edited" in text


async def test_user_edit_action_with_incorrect_input(admin_controller: AdminController):
    user = User(id=123456, username="test")
    register_user(admin_controller.users_repo, user)

    text, kb = await admin_controller.edit_user_action(user.id, "incorrect", "input")
    assert "Error! Key to edit does not exist." in text
    text, kb = await admin_controller.edit_user_action(
        user.id, "unbanned_date", "hello"
    )
    assert "Error! This key can't be edited in this way"
