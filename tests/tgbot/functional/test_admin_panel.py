from datetime import datetime, timedelta

from pyrogram.client import Client
from sqlalchemy.orm import Session

from config import config
from tgbot.misc.generate_id import generate_base_id
from tgbot.models.adverts import Advert, AdvertisementsRepository
from tgbot.models.users import User, UsersRepository
from .utils import assert_last_messsage_text_in


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
            client, config.tg_bot.bot_name, f"Not a Telegram ID or username"
        )

        # Test user not found
        await client.send_message(config.tg_bot.bot_name, f"/finduser 456")
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, f"User was not found"
        )
