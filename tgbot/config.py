from dataclasses import dataclass

from environs import Env

from tgbot import data


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    tables: list
    auth: dict


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool
    message_contents: list


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            message_contents=data.content
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
            tables=data.db_tables,
            # for pgsqlighter auth argument
            auth={ 
                'user': env.str('DB_USER'),
                'host': env.str('DB_HOST'),
                'password': env.str('DB_PASS'),
                'port': env.str('DB_PORT')
                }
        ),
        misc=Miscellaneous()
    )
