import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from pyrogram.client import Client
import pytest
from sqlalchemy.orm import Session

from config import config
from tgbot.misc.generate_id import generate_base_id
from tgbot.models.adverts import Advert, AdvertisementsRepository
from tgbot.models.users import User, UsersRepository
from .utils import assert_last_messsage_text_in, wait


async def ensure_tgclient_is_admin(client: Client):
    user_id = (await client.get_me()).id
    if user_id not in config.tg_bot.admin_ids:
        config.tg_bot.admin_ids.append(user_id)


async def test_admin_panel_start(telegram_client: Client):
    async with telegram_client as client:
        await ensure_tgclient_is_admin(client)
        await client.send_message(config.tg_bot.bot_name, "/adm")
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, "Hello, admin!"
        )


async def register_user(session: Session, user_id=generate_base_id(), username="test"):
    user = User(id=user_id, username=username)
    UsersRepository(session).add(user)
    session.commit()
    return user


async def test_admin_stats_panel_intro(telegram_client: Client, session):
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        await ensure_tgclient_is_admin(client)
        await register_user(session, user_id)

        await client.send_message(config.tg_bot.bot_name, "/adm_stats")

        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            f"Statistics of the {config.tg_bot.bot_name}",
        )
        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            str(user_id),
        )


async def test_admin_users_panel_intro(telegram_client: Client, session):
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        await ensure_tgclient_is_admin(client)
        await register_user(session, user_id)

        await client.send_message(config.tg_bot.bot_name, "/adm_users")

        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            f"The {config.tg_bot.bot_name} users panel",
        )
        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            str(user_id),
        )


async def test_admin_advertisements_panel_intro(telegram_client: Client, session):
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        await register_user(session, user_id)
        await ensure_tgclient_is_admin(client)

        advertisement = Advert(
            id=generate_base_id(),
            header="Test advert",
            content={"text": "random text"},
            created_by=user_id,
            sending_dates={datetime.now() + timedelta(days=1): False},
        )
        AdvertisementsRepository(session).add(advertisement)
        session.commit()

        await client.send_message(config.tg_bot.bot_name, "/adm_advertisements")

        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            f"The advert panel of the {config.tg_bot.bot_name}",
        )
        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            str(advertisement.id),
        )


async def test_find_user_action(telegram_client: Client, session):
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        await register_user(session, user_id)
        await ensure_tgclient_is_admin(client)

        # Test finding user by id and after `await State.set()`
        await client.send_message(config.tg_bot.bot_name, f"/finduser")
        await assert_last_messsage_text_in(
            client,
            config.tg_bot.bot_name,
            "Enter the ID or username of the user",
        )
        await client.send_message(config.tg_bot.bot_name, str(user_id))
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, f"User Information {user_id}"
        )

        # Test finding user by username
        await client.send_message(config.tg_bot.bot_name, f"/finduser test")
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, f"User Information {user_id}"
        )

        # Test invalid input
        await client.send_message(config.tg_bot.bot_name, f"/finduser invalid input")
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, f"User was not found"
        )

        # Test user not found
        await client.send_message(config.tg_bot.bot_name, f"/finduser 456")
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, f"User was not found"
        )


@pytest.fixture()
def user_for_ban(session):
    user = User(id=123456, username="test2")
    UsersRepository(session).add(user)
    session.commit()
    yield user


@wait
async def assert_mocked_answer_in(mock_send: AsyncMock, chat_id, text):
    assert mock_send.await_args
    assert mock_send.await_args[0][0] == chat_id and text in mock_send.await_args[0][1]


@patch("aiogram.Bot.send_message")
async def test_ban_user(mock_send, user_for_ban, session, telegram_client: Client):
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        await register_user(session, user_id)
        await ensure_tgclient_is_admin(client)

        # Test incorrect input
        await client.send_message(config.tg_bot.bot_name, f"/ban")
        await assert_mocked_answer_in(mock_send, user_id, "Incorrect syntax.")

        # Test user_id and time-specification input
        await client.send_message(config.tg_bot.bot_name, f"/ban {user_for_ban.id} 1m")
        await assert_mocked_answer_in(
            mock_send, user_id, f"User @{user_for_ban.username} has been banned until"
        )

        # Test nickname and no time-specification input
        await client.send_message(config.tg_bot.bot_name, f"/ban {user_for_ban.id} 2")
        await assert_mocked_answer_in(
            mock_send, user_id, f"User @{user_for_ban.username} has been banned until"
        )

        # Test permanent ban
        await client.send_message(config.tg_bot.bot_name, f"/ban {user_for_ban.id}")
        await assert_mocked_answer_in(
            mock_send,
            user_id,
            f"User @{user_for_ban.username} has been banned until",
        )
        mock_send.await_args_list = []

        # Test user not found
        await client.send_message(config.tg_bot.bot_name, "/ban 456")
        await assert_mocked_answer_in(
            mock_send,
            user_id,
            f"User to ban was not found",
        )
        mock_send.await_args_list = []

        # Ensure user have receiving notice after ban
        await client.send_message(config.tg_bot.bot_name, f"/ban {user_for_ban.id}")
        await asyncio.sleep(2)
        assert (
            mock_send.await_args_list[-2][0][0] == user_for_ban.id
            and "You were banned" in mock_send.await_args_list[-2][0][1]
        )

        mock_send.await_args_list = []

# TODO: at this moment i has decided to write unittests only
