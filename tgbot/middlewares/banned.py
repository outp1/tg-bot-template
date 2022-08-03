import asyncio
from typing import Union
from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher.middlewares import BaseMiddleware
import pytz
from aiogram.dispatcher.handler import CancelHandler, current_handler

class BannedMiddlware(BaseMiddleware):

    def __init__(self):
        super(BannedMiddlware, self).__init__()

    async def pre_process(self, obj, *args):
        if obj.get('from_user'):
            user_tables = obj.bot.get('user_tables')
            user = await user_tables.take_user('user_id', obj.get('from_user').get('id'))
            if user['unbanned_date'] < datetime.now(pytz.timezone('Europe/Moscow')):
                logger = obj.bot.get('logger')
                logger.info('CANCELLED HANDLER')
                raise CancelHandler
