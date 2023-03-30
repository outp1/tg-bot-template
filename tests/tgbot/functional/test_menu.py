from sqlalchemy.orm import Session
from pyrogram.client import Client

from tgbot.models.orm.users import UserModel
from .utils import assert_last_messsage_text_in
from config import config


async def test_user_registering_at_start(session: Session, telegram_client: Client):
    async with telegram_client as client:
        await client.send_message(text="/start", chat_id=config.tg_bot.bot_name)
        await assert_last_messsage_text_in(
            client, config.tg_bot.bot_name, "Добро пожаловать"
        )

        user_id = (await client.get_me()).id
        assert session.query(UserModel).get(user_id)
