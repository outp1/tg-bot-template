from dataclasses import dataclass
from typing import Optional

from environs import Env
from aiogram.types import InlineKeyboardButton

from tgbot import data


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    port: int
    database: str
    tables: list


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    admin_panel_buttons: list[InlineKeyboardButton]
    use_redis: bool
    message_contents: list
    bot_name: str


@dataclass
class Program:
    logs_folder: str
    logs_file: str
    logs_console_level: str
    logs_token: str
    logs_telegram_id: str
    timezone: str


@dataclass
class Miscellaneous:
    inclose_text: str
    support_mention: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous
    program: Program


def load_config(path: Optional[str] = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            admin_panel_buttons=data.admin_panel_buttons,
            use_redis=env.bool("USE_REDIS"),
            message_contents=data.content,
            bot_name=env.str("BOT_NAME")
        ),
        db=DbConfig(
            host=env.str("POSTGRES_HOST"),
            password=env.str("POSTGRES_PASSWORD"),
            user=env.str("POSTGRES_USER"),
            port=env.str("POSTGRES_PORT"),
            database=env.str("POSTGRES_DB"),
            tables=data.db_tables,
        ),
        program=Program(
            logs_folder=env.str("LOGS_FOLDER"),
            logs_file=env.str("LOGS_FILE"),
            logs_console_level=env.str("LOGS_CONSOLE_LEVEL"),
            logs_token=env.str("LOGS_TOKEN"),
            logs_telegram_id=env.str("LOGS_TELEGRAM_ID"),
            timezone=env.str("TZ"),
        ),
        misc=Miscellaneous(
            inclose_text=env.str("INCLOSE_TEXT"),
            support_mention=env.str("SUPPORT_MENTION"),
        ),
    )


config: Config
config = load_config()
