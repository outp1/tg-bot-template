import pytest

from tgbot.controllers import MenuController, AdminController


@pytest.fixture
def menu_controller(session, db_repository):
    yield MenuController(session, db_repository)


@pytest.fixture()
def admin_controller(session, db_repository):
    yield AdminController(session, db_repository)
