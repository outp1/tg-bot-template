from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
import sys


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        data["user_tables"] = obj.bot.get('user_tables')
        data["content_tables"] = obj.bot.get('content_tables')

        # Передаем данные из таблицы в хендлер
        # data['some_model'] = await Model.get()
