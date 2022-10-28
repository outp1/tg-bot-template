from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
import sys


class ObjectsMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        data["bot"] = obj.bot
        data["config"] = obj.bot.get('config')
        data["logger"] = obj.bot.get('logger')
        data["user_tables"] = obj.bot.get('user_tables')
        data["content_tables"] = obj.bot.get('content_tables')
        data["modhistory_tables"] = obj.bot.get('modhistory_tables')
        data["advertising_tables"] = obj.bot.get('advertising_tables')

        # Передаем данные из таблицы в хендлер
        # data['some_model'] = await Model.get()
