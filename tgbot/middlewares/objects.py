from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class ObjectsMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        data["bot"] = obj.bot
        data["dp"] = obj.bot.get("dp")

        #  controllers
        data["menu_controller"] = obj.bot.get("menu_controller")
