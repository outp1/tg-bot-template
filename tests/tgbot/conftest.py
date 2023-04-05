import asyncio
import inspect

import pytest
from pyrogram.client import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists, drop_database

from bot import init_repository, setup_tgbot
from tgbot.controllers.menu import MenuController
from tgbot.models.orm.base import Base
from config import config
from utils.botlogging import prepare_logging

prepare_logging()


@pytest.fixture
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop


def pytest_collection_modifyitems(config, items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture
def setup_bot(event_loop):
    config.db.database = "test"
    task = event_loop.create_task(setup_tgbot())
    yield
    task.cancel()


@pytest.fixture
def database():
    login_data = (
        f"{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}"
    )
    engine = create_engine(f"postgresql://{login_data}/test")
    try:
        if database_exists(engine.url):
            drop_database(engine.url)
        create_database(engine.url)
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        yield engine
    finally:
        drop_database(engine.url)


@pytest.fixture
def session(database):
    sess = Session(database)
    yield sess
    sess.close()


@pytest.fixture
def db_repository(session):
    yield init_repository(session)


@pytest.fixture
def telegram_client(setup_bot):
    # At the first setup add flag -s to enable telegram login
    client = Client(
        "test-data.test_client",
        api_id=config.tests.api_id,
        api_hash=config.tests.api_hash,
    )
    yield client
