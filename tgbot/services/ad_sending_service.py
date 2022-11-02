import logging
import datetime
import asyncio
import traceback

import pytz
from aiogram.bot import Bot
from aiogram import types

from tgbot.models.admin_models import AdvertisingTables
from tgbot.models.user_models import UserTables


class AdSendingService:
    
    def __init__(self, ad_tables: AdvertisingTables, user_tables: UserTables, bot: Bot,
            logger: logging.Logger):
        self.ad_tables = ad_tables
        self.user_tables = user_tables
        self.bot = bot
        self.logger = logger

    async def start(self, polling_delay: int):
        while True:
            now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            advertisements = await self.ad_tables.get_all_advertisements()
            for ad in advertisements:
                try:
                    sending_date = ad['sending_date']
                    if ((now >= sending_date) and (ad['sending_status'] == False)):
                        await self.start_mailing(ad)
                        self.logger.info(f'Mailing with ID - {ad["advert_id"]} started')
                except TypeError:
                    pass
                except AttributeError:
                    pass
            await asyncio.sleep(polling_delay)

    async def start_mailing(self, advert):
        users = await self.user_tables.take_all_users()
        for user in users:
            try:
                await self.send_message(advert, user['user_id'])
                await self.ad_tables.update_advertising(advert['advert_id'], 'sending_status', True)
            except:
                pass
        self.logger.info(f'Mailing with ID {advert["advert_id"]} ended')

    async def send_message(self, advert, user_id):
        if advert['inline_buts']:
            if type(advert['inline_buts']) is dict:
                kb = types.InlineKeyboardMarkup()
                _type_value = {advert['inline_buts']['_type']: advert['inline_buts']['content']}
                kb.add(types.InlineKeyboardButton(text=advert['text'], **_type_value))
            else:
                kb = types.InlineKeyboardMarkup()
                for b in advert['inline_buts']:
                    _type_value = {b['_type']: b['content']}
                    kb.add(types.InlineKeyboardButton(text=b['text'], **_type_value))
        else:
            kb = types.InlineKeyboardMarkup()
        if advert['media_type'] == 'media_group':
            medias = []
            for obj in advert['media']:
                medias.append(obj)
            medias[0]['caption'] = advert['text'] 
            media_group = types.MediaGroup()
            media_group.attach_many(*medias)
            await self.bot.send_media_group(chat_id=user_id, media=media_group)
        elif advert['media_type'] == 'photo':
            await self.bot.send_photo(chat_id=user_id, photo=advert['media'], caption=advert['text'], reply_markup=kb)
        elif advert['media_type'] == 'video':
            await self.bot.send_video(chat_id=user_id, video=advert['media'], caption=advert['text'], reply_markup=kb)
        elif advert['media_type'] == 'document':
            await self.bot.send_document(chat_id=user_id, document=advert['document'], caption=advert['text'], reply_markup=kb)
        else: 
            await self.bot.send_message(chat_id=user_id, text=advert['text'], reply_markup=kb)

