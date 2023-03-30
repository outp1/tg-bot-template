import pytest

from tgbot.controllers import MenuController
from bot import init_repository


@pytest.fixture
def menu_controller(session):
    yield MenuController(session, init_repository(session))
