from tgbot.controllers.menu import MenuController
from tgbot.misc.generate_id import generate_base_id
from tgbot.models.users import User


async def test_register_user(menu_controller: MenuController):
    user = User(id=generate_base_id(), username="test")
    await menu_controller.register_user(user)

    assert user.id in menu_controller.db_repository["users"]
