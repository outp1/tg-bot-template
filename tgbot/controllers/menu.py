from sqlalchemy.orm import Session

from tgbot.keyboards.reply import get_menu_keyboard
from tgbot.models.users import User, UsersRepository


class MenuController:
    def __init__(self, session: Session, db_repository: dict):
        self.session = session
        self.db_repository = db_repository
        self.users_repo = UsersRepository(session, db_repository)

    async def register_user(self, user: User):
        if not self.users_repo.get_by_id(user.id):
            self.users_repo.add(user)
            self.session.commit()

    async def get_start_data(self):
        text = "Добро пожаловать!"
        return text, get_menu_keyboard()

    async def get_user_info(self, user_id):
        return self.users_repo.get_by_id(user_id)
